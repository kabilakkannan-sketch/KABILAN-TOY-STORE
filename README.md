# 🧸 KK SHOPPING - Premium Kids E-Commerce Platform

A comprehensive, full-stack E-Commerce web application designed for ordering kids' toys and interactive electronics. This platform delivers a seamless shopping experience for users while offering a data-driven analytical dashboard for administrators to monitor business metrics.

## 🚀 Key Features

### 👤 User-End Capabilities
* **Flexible Purchasing Options:** Users can instantly buy a single product via direct checkout or purchase multiple items simultaneously using the integrated "Add to Cart" management system.
* **Mandatory Online Payments:** Secure transaction processing that enforces mandatory online payment settlement before an order is officially placed.
* **Automated Refund & Wallet System:** A dedicated user wallet inside the homepage enabling instant deposit, withdrawal, and automated money refunds immediately upon processing an order return.
* **Advanced Multi-Image Gallery:** Supports uploading 4 to 5 high-resolution images per product, allowing users to interactively **Zoom In and Zoom Out** to inspect item details thoroughly.
* **Real-Time Admin Chat Integration:** Built-in messaging system enabling users to chat directly with the admin regarding product doubts and receive instant support solutions.
* **Verified Reviews & Star Ratings:** A comprehensive feedback mechanism where customers can provide descriptive reviews and performance ratings exclusively for delivered products.

### 👑 Administrative Control Panel (Dashboard)
* **Live Revenue Analytics Dashboard:** A centralized business console visualizing crucial data points, including total gross revenue, overall performance metrics, and order frequencies.
* **Inventory & Trend Tracking:** Automated ranking tools displaying the most frequently purchased products and top-selling toy categories.
* **Interactive Customer Query Resolution:** An administrative chat interface to view ongoing user queries regarding products and reply to them in real time.
* **Return & Logistics Management:** Dedicated monitoring system to view, track, and process customer-returned products efficiently.
* **Consolidated Order & Feedback Tracking:** Complete structural visibility into total orders placed and direct user feedback reviews.
* **Dynamic Bulk Multi-Image Uploads:** Allows the admin to upload 4 to 5 product display images at a single time during new inventory entry.

## 🛠️ Tech Stack & Architecture
* **Backend Framework:** Python & Django (Strict compliance with MVC/MVT architecture)
* **Database Engine:** Relational SQLite Database (`db.sqlite3`) / PostgreSQL production support
* **Frontend Interface:** HTML5, CSS3, JavaScript, and Font Awesome Premium UI Icons
* **Session Management:** Secure server-side session state validation for user authentication

## 🔐 Demo Credentials
> 💡 **Note for HR / Technical Interviewers:** To evaluate the structural functionalities of both the User Side and the Administrative Panels locally, you may utilize the pre-configured credential data:
* **Admin Username:** `kabilan`
* **Admin Password:** `1234` *(Kindly replace this with your actual local demo password)*

## 🏃‍♂️ Local Setup Instructions
To run this project locally, execute the following commands sequentially in your terminal:
```bash
# Clone the repository source tree
git clone [https://github.com/kabilakkannan-sketch/KABILAN-TOY-STORE.git](https://github.com/kabilakkannan-sketch/KABILAN-TOY-STORE.git)

# Navigate to the project root directory
cd kabi_final

# Apply structural database migrations
python manage.py makemigrations
python manage.py migrate

# Launch the local development hosting server
python manage.py runserver