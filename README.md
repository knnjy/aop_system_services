# aop_system_services
Monolith Service for Automated Order Processing (AOP) System

SERVICES (API)
1. Authentication & Identity Service – Manages login and identity verification. Get user information.
2. Catalog Management Service – Handle fetching and updating product lists and information.
3. Order Management Service – Handles requests, approvals, and order tracking.
4. Payment Service – Handle communication between OPS and the Cashier System. Processes payments and receipts. 

## FOLDER STRUCTURE (Layered Architecture)

🧩 Controller Layer
Role: Entry point for handling HTTP requests.
Responsibility: Receives input from clients (API calls), validates basic request data, and forwards it to the service layer.

⚙️ Service Layer
Role: Contains business logic.
Responsibility: Processes data, applies rules, coordinates between DAO and controller, and ensures workflows are executed correctly.

📂 DAO Layer
Role: Data Access Object layer.
Responsibility: Handles database operations (CRUD). Abstracts persistence logic from business logic.

📑 Model Layer
Role: Defines domain entities or data structures.
Responsibility: Represents the shape of your data (e.g., Book, User, Order).

🔄 DTO Layer
Role: Data Transfer Object layer.
Responsibility: Shapes and transfers data between layers or systems, often simplifying or securing what gets exposed to the client.

🛠️ Utils Layer
Role: Provides reusable helper functions.
Responsibility: Common utilities like date formatting, validation, or encryption.

