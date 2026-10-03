import sys


class Product:
    """Represents an individual product item with pricing and stock details."""

    def __init__(self, product_id: str, name: str, stock: int, purchase_price: float, selling_price: float):
        self.product_id = product_id
        self.name = name
        self.stock = int(stock)
        self.purchase_price = float(purchase_price)
        self.selling_price = float(selling_price)

    @property
    def total_valuation(self) -> float:
        """Calculates total valuation based on selling price."""
        return self.stock * self.selling_price

    def merge_with(self, other: 'Product') -> 'Product':
        """
        Merges two product records with conflicting IDs:
        - Combines stock quantities.
        - Preserves lower purchase price.
        - Preserves higher selling price.
        """
        if self.product_id != other.product_id:
            raise ValueError("Cannot merge products with different IDs.")

        new_stock = self.stock + other.stock
        new_purchase_price = min(self.purchase_price, other.purchase_price)
        new_selling_price = max(self.selling_price, other.selling_price)

        return Product(
            product_id=self.product_id,
            name=self.name,  # Retain existing name
            stock=new_stock,
            purchase_price=new_purchase_price,
            selling_price=new_selling_price
        )

    def __repr__(self):
        # Format integer prices cleanly if applicable
        p_price = int(self.purchase_price) if self.purchase_price.is_integer() else self.purchase_price
        s_price = int(self.selling_price) if self.selling_price.is_integer() else self.selling_price
        return f"{self.product_id} {self.name} stock={self.stock} purchase={p_price} selling={s_price}"


class Inventory:
    """Manages a collection of Product entities and supports operator overloading."""

    def __init__(self, name: str = "Default"):
        self.name = name
        # Dictionary mapping product_id -> Product object
        self.products = {}

    def add_product(self, product: Product):
        """Adds a product or merges stock if product_id already exists."""
        if product.product_id in self.products:
            self.products[product.product_id] = self.products[product.product_id].merge_with(product)
        else:
            self.products[product.product_id] = product

    def delete_product(self, product_id: str) -> bool:
        """Deletes a product by ID. Returns True if successful."""
        if product_id in self.products:
            del self.products[product_id]
            return True
        return False

    def update_stock(self, product_id: str, new_stock: int) -> bool:
        """Updates stock quantity for a given product ID."""
        if product_id in self.products:
            self.products[product_id].stock = int(new_stock)
            return True
        return False

    def get_total_valuation(self) -> float:
        """Calculates total inventory valuation across all products."""
        return sum(p.total_valuation for p in self.products.values())

    # --- Operator Overloading Methods ---

    def __add__(self, other: 'Inventory') -> 'Inventory':
        """
        Overloads the '+' operator to merge two inventories.
        Conflict Rule: Combines stock, keeps min purchase price & max selling price.
        """
        merged_inventory = Inventory(f"{self.name}+{other.name}")

        # Add all items from self
        for prod in self.products.values():
            merged_inventory.add_product(
                Product(prod.product_id, prod.name, prod.stock, prod.purchase_price, prod.selling_price)
            )

        # Merge all items from other
        for prod in other.products.values():
            merged_inventory.add_product(
                Product(prod.product_id, prod.name, prod.stock, prod.purchase_price, prod.selling_price)
            )

        return merged_inventory

    def __lt__(self, other: 'Inventory') -> bool:
        """Overloads '<' operator to compare inventories by total valuation."""
        return self.get_total_valuation() < other.get_total_valuation()

    def __eq__(self, other: 'Inventory') -> bool:
        """Overloads '==' operator to compare inventories by total valuation."""
        return self.get_total_valuation() == other.get_total_valuation()

    def __gt__(self, other: 'Inventory') -> bool:
        """Overloads '>' operator to compare inventories by total valuation."""
        return self.get_total_valuation() > other.get_total_valuation()

    def display_summary(self):
        """Prints products sorted lexicographically by product_id."""
        for prod_id in sorted(self.products.keys()):
            print(self.products[prod_id])


# --- Helper Parsing Functions ---

def load_inventory_from_lines(lines: list, name: str) -> Inventory:
    inv = Inventory(name)
    for line in lines:
        parts = line.strip().split()
        if len(parts) == 5:
            pid, pname, stock, p_price, s_price = parts
            prod = Product(pid, pname, int(stock), float(p_price), float(s_price))
            inv.add_product(prod)
    return inv


def process_inventory_operations():
    """
    Sample Driver demonstrating ADD, DELETE, UPDATE, MERGE, and COMPARE operations.
    """
    # Sample setup matching problem specification
    lines_a = ["P1 Pen 10 5 8"]
    lines_b = ["P1 Pen 7 4 9"]

    inv_a = load_inventory_from_lines(lines_a, "A")
    inv_b = load_inventory_from_lines(lines_b, "B")

    # Perform MERGE using overloaded '+' operator
    merged_inv = inv_a + inv_b
    merged_inv.display_summary()


if __name__ == "__main__":
    process_inventory_operations()
