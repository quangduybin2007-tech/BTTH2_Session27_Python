from abc import ABC, abstractmethod

# ==========================================
# 1. CARRIER CLASSES (Duck Typing Showcase)
# ==========================================

class FedExCarrier:
    """Đối tác vận chuyển FedEx độc lập."""
    def ship_package(self, product, quantity):
        print(f"[Hệ thống FedEx]: Đang tiếp nhận mã sản phẩm {product.product_code}...")
        product.export_stock(quantity)
        return True

class DHLCarrier:
    """Đối tác vận chuyển DHL độc lập."""
    def ship_package(self, product, quantity):
        print(f"[Hệ thống DHL]: Đang xử lý bàn giao lô hàng cho mã {product.product_code}...")
        product.export_stock(quantity)
        return True


# ==========================================
# 2. INVENTORY MANAGEMENT CLASSES (OOP Core)
# ==========================================

class BaseProduct(ABC):
    """
    Abstract Base Class định nghĩa bộ khung chuẩn cho mọi loại hàng hóa trong kho.
    @abstractmethod: Bắt buộc các lớp con phải hiện thực hóa phương thức cụ thể.
    """
    warehouse_name = "Amazon Logistics"
    base_storage_fee = 5000

    def __init__(self, product_code, product_name, initial_stock=0):
        if not self.validate_product_code(product_code):
            raise ValueError("Mã sản phẩm không hợp lệ! Phải bắt đầu bằng chữ và có đúng 10 ký tự.")
        
        self._product_code = product_code
        self._product_name = " ".join(product_name.strip().split()).upper()
        # Đóng gói nghiêm ngặt bằng thuộc tính private __stock_quantity (Bẫy 1 gián tiếp)
        self.__stock_quantity = int(initial_stock)

    @property
    def product_code(self):
        """Getter cho mã sản phẩm."""
        return self._product_code

    @property
    def product_name(self):
        """Getter cho tên sản phẩm."""
        return self._product_name

    @product_name.setter
    def product_name(self, name):
        """Setter tự động chuẩn hóa tên sản phẩm (In hoa, xóa khoảng trắng thừa)."""
        self._product_name = " ".join(name.strip().split()).upper()

    @property
    def stock_quantity(self):
        """@property: Cho phép đọc số lượng tồn kho hiện tại, không có setter trực tiếp."""
        return self.__stock_quantity

    def _set_stock_quantity(self, quantity):
        """Phương thức nội bộ để cập nhật số lượng kho một cách an toàn."""
        self.__stock_quantity = int(quantity)

    @abstractmethod
    def import_stock(self, quantity):
        """Phương thức trừu tượng nhập kho hàng."""
        pass

    @abstractmethod
    def export_stock(self, quantity):
        """Phương thức trừu tượng xuất kho hàng."""
        pass

    @staticmethod
    def validate_product_code(product_code):
        """@staticmethod: Kiểm tra mã sản phẩm phải bắt đầu bằng chữ và dài đúng 10 ký tự."""
        return isinstance(product_code, str) and len(product_code) == 10 and product_code[0].isalpha() and product_code.isalnum()

    @classmethod
    def update_warehouse_name(cls, new_name):
        """@classmethod: Cập nhật tên chuỗi kho hàng trên toàn bộ hệ thống."""
        cls.warehouse_name = new_name

    # --- Operator Overloading ---
    def __add__(self, other):
        """Nạp chồng toán tử cộng (+). Bẫy số 3: Kiểm tra kiểu dữ liệu kế thừa phù hợp."""
        if not isinstance(other, BaseProduct):
            return NotImplemented
        return self.stock_quantity + other.stock_quantity

    def __lt__(self, other):
        """Nạp chồng toán tử so sánh (<). Bẫy số 3: Kiểm tra kiểu dữ liệu kế thừa phù hợp."""
        if not isinstance(other, BaseProduct):
            return NotImplemented
        return self.stock_quantity < other.stock_quantity


class ColdStorageProduct(BaseProduct):
    """Lớp quản lý hàng hóa đông lạnh cần duy trì nhiệt độ nghiêm ngặt."""
    def __init__(self, product_code, product_name, required_temperature, initial_stock=0):
        # Sử dụng super().__init__() để kế thừa thuộc tính từ lớp cha
        super().__init__(product_code, product_name, initial_stock)
        self.required_temperature = float(required_temperature)

    def import_stock(self, quantity):
        """Ghi đè phương thức nhập kho tiêu chuẩn."""
        if quantity <= 0:
            raise ValueError("Số lượng nhập kho phải lớn hơn 0.")
        self._set_stock_quantity(self.stock_quantity + quantity)

    def export_stock(self, quantity):
        """Ghi đè phương thức xuất kho, chịu thêm 5% phí hao hụt bảo quản phụ trội."""
        if quantity <= 0:
            raise ValueError("Số lượng xuất kho phải lớn hơn 0.")
        
        loss_quantity = quantity * 0.05
        total_deduction = quantity + loss_quantity
        
        if self.stock_quantity - total_deduction < 0:
            raise ValueError("Số lượng tồn kho không đủ để đáp ứng đơn xuất và lượng hao hụt phát sinh.")
        
        self._set_stock_quantity(self.stock_quantity - total_deduction)
        return loss_quantity

    def apply_cooling_cost(self):
        """Tính toán chi phí vận hành làm lạnh phát sinh dựa trên tồn kho thực tế."""
        cooling_cost = self.stock_quantity * abs(self.required_temperature) * 50
        return cooling_cost


class HazardousProduct(BaseProduct):
    """Lớp quản lý hàng hóa nguy hiểm giới hạn mức lưu trữ an toàn."""
    def __init__(self, product_code, product_name, max_safety_limit, initial_stock=0):
        super().__init__(product_code, product_name, initial_stock)
        self.max_safety_limit = int(max_safety_limit)

    def import_stock(self, quantity):
        """
        Ghi đè phương thức nhập kho. 
        Bẫy số 2: Ngăn chặn vượt giới hạn tồn kho an toàn khu vực.
        """
        if quantity <= 0:
            raise ValueError("Số lượng nhập kho phải lớn hơn 0.")
        if self.stock_quantity + quantity > self.max_safety_limit:
            raise ValueError(f"Giao dịch thất bại! Số lượng nhập vào khiến tồn kho vượt quá hạn mức an toàn cho phép (Tối đa: {self.max_safety_limit}).")
        
        self._set_stock_quantity(self.stock_quantity + quantity)

    def export_stock(self, quantity):
        """Ghi đè phương thức xuất kho an toàn."""
        if quantity <= 0:
            raise ValueError("Số lượng xuất kho phải lớn hơn 0.")
        if self.stock_quantity - quantity < 0:
            raise ValueError("Số lượng hàng tồn kho không đủ để xuất.")
        
        self._set_stock_quantity(self.stock_quantity - quantity)


class HybridPremiumProduct(ColdStorageProduct, HazardousProduct):
    """Dòng sản phẩm lai cao cấp kế thừa tính chất từ cả ColdStorage và Hazardous."""
    def __init__(self, product_code, product_name, required_temperature, max_safety_limit, initial_stock=0):
        # Thiết lập khởi tạo đa kế thừa đồng bộ qua chuỗi MRO
        ColdStorageProduct.__init__(self, product_code, product_name, required_temperature, initial_stock)
        HazardousProduct.__init__(self, product_code, product_name, max_safety_limit, initial_stock)

    def import_stock(self, quantity):
        """Tích hợp kiểm tra an toàn từ HazardousProduct trước khi cho phép nhập kho."""
        HazardousProduct.import_stock(self, quantity)

    def export_stock(self, quantity):
        """Tích hợp tính toán hao hụt từ ColdStorageProduct khi xuất kho hàng."""
        return ColdStorageProduct.export_stock(self, quantity)


# ==========================================
# 3. GLOBAL DISPATCH SYSTEM (Duck Typing Engine)
# ==========================================

def dispatch_to_carrier(carrier_agent, product, quantity):
    """
    Hàm toàn cục ứng dụng Duck Typing linh hoạt điều phối vận chuyển.
    Bẫy số 4: Bắt lỗi AttributeError nếu đối tượng truyền vào không cấu hình hàm kĩ thuật chuẩn.
    """
    try:
        if not hasattr(carrier_agent, 'ship_package'):
            raise AttributeError("Đơn vị vận chuyển không hợp lệ hoặc chưa ký kết hợp đồng kỹ thuật.")
        
        return carrier_agent.ship_package(product, quantity)
    except AttributeError as e:
        print(f"Lỗi hệ thống: {e}")
        return False
    except Exception as e:
        print(f"Điều phối thất bại! Lý do: {e}")
        return False


# ==========================================
# 4. CLI INTERFACE MENU SYSTEM
# ==========================================

def main():
    products = []
    current_product = None

    # Khởi tạo sẵn một lô hàng đối ứng mẫu trong hệ thống để test tính năng gộp lô (Menu 5)
    backup_prod = ColdStorageProduct("AMZ9999999", "BEEF STEAK", -18, 350)
    products.append(backup_prod)

    while True:
        print("\n===== AMAZON INVENTORY SIMULATOR PRO =====")
        print("1. Đăng ký mã hàng hóa mới (Chọn loại sản phẩm)")
        print("2. Xem thông tin & Kiểm tra thứ tự kế thừa (MRO)")
        print("3. Giao dịch Nhập / Xuất kho (Đa hình)")
        print("4. Kiểm tra điều kiện bảo quản / Tính chi phí phụ trội")
        print("5. Kiểm tra tính năng gộp lô hàng & So sánh tồn kho (Overloading)")
        print("6. Điều phối vận chuyển qua Đối tác thứ ba (Duck Typing)")
        print("7. Thoát chương trình")
        print("==========================================")
        
        choice = input("Chọn chức năng (1-7): ").strip()

        if choice == "1":
            print("\n--- CHỌN LOẠI SẢN PHẨM KHỞI TẠO ---")
            print("1. Cold Storage Product (Hàng Đông Lạnh)")
            print("2. Hazardous Product (Hàng Nguy Hiểm)")
            print("3. Hybrid Premium Product (Hàng Lai Cao Cấp)")
            type_choice = input("Chọn loại sản phẩm (1-3): ").strip()
            
            prod_code = input("Nhập mã sản phẩm 10 ký tự: ").strip()
            if not BaseProduct.validate_product_code(prod_code):
                print("Mã sản phẩm không hợp lệ! Phải gồm đúng 10 ký tự.")
                continue

            name = input("Nhập tên sản phẩm: ")
            
            try:
                if type_choice == "1":
                    temp = float(input("Nhập nhiệt độ bảo quản yêu cầu (độ C): "))
                    current_product = ColdStorageProduct(prod_code, name, temp, 100) # Khởi tạo mẫu 100 đơn vị
                    print(f"Đăng ký sản phẩm Đông Lạnh thành công!\nTên sản phẩm: {current_product.product_name}")
                elif type_choice == "2":
                    limit = int(input("Nhập hạn mức lưu trữ an toàn tối đa: "))
                    current_product = HazardousProduct(prod_code, name, limit, 100) # Khởi tạo mẫu 100 đơn vị
                    print(f"Đăng ký sản phẩm Nguy Hiểm thành công!\nTên sản phẩm: {current_product.product_name}")
                elif type_choice == "3":
                    temp = float(input("Nhập nhiệt độ bảo quản yêu cầu (độ C): "))
                    limit = int(input("Nhập hạn mức lưu trữ an toàn tối đa: "))
                    current_product = HybridPremiumProduct(prod_code, name, temp, limit, 100) # Khởi tạo mẫu 100 đơn vị
                    print(f"Đăng ký sản phẩm Lai Cao Cấp thành công!\nTên sản phẩm: {current_product.product_name}")
                else:
                    print("Lựa chọn loại sản phẩm không hợp lệ.")
                    continue
                
                products.append(current_product)
            except Exception as e:
                print(f"Lỗi đăng ký: {e}")

        elif choice == "2":
            if not current_product:
                print("Hệ thống chưa có thông tin sản phẩm. Vui lòng đăng ký ở Chức năng 1 trước.")
                continue
            
            print("\n--- THÔNG TIN SẢN PHẨM HIỆN TẠI ---")
            print(f"Loại sản phẩm: {type(current_product).__name__}")
            print(f"Chuỗi kho: {current_product.warehouse_name}")
            print(f"Mã sản phẩm: {current_product.product_code}")
            print(f"Tên sản phẩm: {current_product.product_name}")
            print(f"Số lượng tồn kho: {current_product.stock_quantity} đơn vị")
            
            if hasattr(current_product, 'required_temperature'):
                print(f"Nhiệt độ yêu cầu: {current_product.required_temperature} độ C")
            if hasattr(current_product, 'max_safety_limit'):
                print(f"Hạn mức an toàn tối đa: {current_product.max_safety_limit} đơn vị")
            
            print("\n--- KIỂM TRA MRO (Thứ tự tìm kiếm phương thức) ---")
            for idx, cls in enumerate(type(current_product).__mro__):
                print(f" [{idx}]: {cls}")

        elif choice == "3":
            if not current_product:
                print("Hệ thống chưa có thông tin sản phẩm.")
                continue
            
            print("\n--- GIAO DỊCH NHẬP / XUẤT KHO ---")
            print("1. Nhập kho")
            print("2. Xuất kho")
            tx_choice = input("Chọn giao dịch (1-2): ").strip()
            
            try:
                qty = int(input("Nhập số lượng hàng hóa: "))
                if tx_choice == "1":
                    # Đa hình kích hoạt cơ chế chặn hạn mức của dòng Hazardous/Hybrid
                    current_product.import_stock(qty)
                    print(f"Nhập kho thành công! Tồn kho mới: {current_product.stock_quantity} đơn vị.")
                elif tx_choice == "2":
                    # Đa hình kích hoạt cơ chế hao hụt của dòng ColdStorage/Hybrid
                    loss = current_product.export_stock(qty)
                    print(f"Xuất kho thành công!")
                    print(f"Số lượng yêu cầu: {qty} đơn vị")
                    if loss:
                        print(f"Số lượng hao hụt bảo quản (5%): {loss} đơn vị")
                    print(f"Số lượng tồn kho cập nhật: {current_product.stock_quantity} đơn vị.")
            except Exception as e:
                # Bẫy số 2: Đánh chặn mượt mà lỗi vượt ngưỡng an toàn hoặc thiếu hàng xuất
                print(f"Giao dịch thất bại! Lỗi nghiệp vụ: {e}")

        elif choice == "4":
            if not current_product:
                print("Hệ thống chưa có thông tin sản phẩm.")
                continue
            
            if hasattr(current_product, 'apply_cooling_cost'):
                print("\n--- TÍNH PHÍ BẢO QUẢN ĐÔNG LẠNH ---")
                print(f"Số lượng tồn kho hiện tại: {current_product.stock_quantity} đơn vị")
                print(f"Nhiệt độ yêu cầu: {current_product.required_temperature} độ C")
                cost = current_product.apply_cooling_cost()
                print(f"Chi phí làm lạnh phát sinh trong ngày: +{cost:,.0f} VND")
            else:
                print("Tính năng không hỗ trợ! Sản phẩm thông thường không tiêu tốn năng lượng làm mát.")

        elif choice == "5":
            if not current_product:
                print("Hệ thống chưa có thông tin sản phẩm.")
                continue
            
            print("\n--- ĐỒNG BỘ & SO SÁNH TỒN KHO (OPERATOR OVERLOADING) ---")
            print(f"Sản phẩm hiện tại (A): {current_product.product_name} (Tồn kho: {current_product.stock_quantity} đơn vị)")
            print(f"Sản phẩm đối ứng (B): {backup_prod.product_name} (Tồn kho: {backup_prod.stock_quantity} đơn vị)")
            
            # Khởi chạy so sánh (__lt__)
            if current_product < backup_prod:
                print("[Kết quả So sánh (__lt__)]: Tồn kho sản phẩm A ÍT HƠN tồn kho sản phẩm B.")
            else:
                print("[Kết quả So sánh (__lt__)]: Tồn kho sản phẩm A LỚN HƠN HOẶC BẰNG tồn kho sản phẩm B.")
            
            # Khởi chạy cộng gộp (__add__)
            total_sum = current_product + backup_prod
            print(f"[Kết quả Tổng hợp (__add__)]: Tổng số lượng tồn kho của cả 2 mã sản phẩm là: {total_sum} đơn vị.")
            
            # Thử nghiệm kiểm tra Bẫy dữ liệu số 3 (Overloading sai kiểu dữ liệu)
            print("\n[Thử nghiệm Edge Case 3]: Thử cộng sản phẩm với một chuỗi ký tự...")
            try:
                result = current_product + "100_ITEMS"
                if result == NotImplemented:
                    raise TypeError("Không thể thực hiện toán tử cộng giữa thực thể BaseProduct và chuỗi văn bản.")
            except TypeError:
                print(">> Bẫy thành công: Hệ thống bắt lỗi ngoại lệ chuẩn xác và từ chối tính toán tạp chất!")

        elif choice == "6":
            if not current_product:
                print("Hệ thống chưa có thông tin sản phẩm.")
                continue
            
            print("\n--- ĐIỀU PHỐI ĐƠN VỊ VẬN CHUYỂN NGOÀI ---")
            print("1. Vận chuyển qua đối tác FedEx")
            print("2. Vận chuyển qua đối tác DHL")
            print("3. Thử nghiệm Đối tác lỗi kỹ thuật (Không cấu hình hàm ship_package)")
            carrier_choice = input("Chọn đối tác vận chuyển (1-3): ").strip()
            
            try:
                ship_qty = int(input("Nhập số lượng hàng hóa bàn giao: "))
                
                if carrier_choice == "1":
                    carrier = FedExCarrier()
                elif carrier_choice == "2":
                    carrier = DHLCarrier()
                elif carrier_choice == "3":
                    # Lớp giả tạo thiếu phương thức để test bẫy 4
                    class InvalidCarrier: pass
                    carrier = InvalidCarrier()
                else:
                    print("Lựa chọn đối tác không hợp lệ.")
                    continue
                
                # Gọi cơ chế Duck Typing xử lý linh hoạt đơn vị ngoài
                success = dispatch_to_carrier(carrier, current_product, ship_qty)
                if success:
                    print("Xác thực đối tác bằng Duck Typing thành công!")
                    print(f"Đơn vị vận chuyển đã tiếp nhận đơn hàng số lượng: {ship_qty} đơn vị.")
                    print(f"Số lượng tồn kho cập nhật: {current_product.stock_quantity} đơn vị.")
            except Exception as e:
                print(f"Bàn giao thất bại! Lỗi: {e}")

        elif choice == "7":
            print("\nCảm ơn đã sử dụng hệ thống Amazon Inventory Simulator Pro!")
            break
        else:
            print("Chức năng không hợp lệ, vui lòng chọn lại từ 1 đến 7.")


if __name__ == "__main__":
    # Minh họa Edge Case 1: Chặn đứng hành vi khởi tạo trực tiếp Abstract Base Class
    print("[Kiểm tra bảo mật hệ thống] Thử khởi tạo trực tiếp lớp trừu tượng BaseProduct...")
    try:
        corrupted_product = BaseProduct("AMZ9999999", "Fake Item")
    except TypeError as error:
        print(f">> Bẫy thành công 1: Hệ thống kích hoạt phòng vệ lớp trừu tượng! Nội dung lỗi: {error}\n")
        
    # Kích hoạt hệ thống điều hành kho CLI
    main()