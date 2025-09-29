erDiagram
    USER ||--o{ TICKET : "submits"
    USER ||--o{ ORDER : "places"
    USER ||--o{ COMMENT : "writes"
    TICKET ||--o{ COMMENT : "has"
    TICKET }|--|| TICKET_CATEGORY : "belongs to"
    ORDER ||--o{ ORDER_ITEM : "contains"
    PRODUCT ||--o{ ORDER_ITEM : "appears in"
    PRODUCT ||--o{ TICKET : "referenced in"

    USER {
        int id PK
        string username
        string email
        string password_hash
        string role
        string department
        boolean is_active
        datetime created_at
        datetime last_login
    }

    TICKET {
        int id PK
        string title
        text description
        int user_id FK
        string status
        string priority
        int category_id FK
        int product_id FK
        datetime created_at
        datetime updated_at
        datetime resolved_at
        text resolution_notes
    }

    COMMENT {
        int id PK
        text content
        int user_id FK
        int ticket_id FK
        datetime created_at
    }

    TICKET_CATEGORY {
        int id PK
        string name
        string description
    }

    ORDER {
        int id PK
        int user_id FK
        string order_number
        float total_amount
        string status
        datetime order_date
        datetime updated_at
        string shipping_address
        string billing_address
        string payment_method
    }

    ORDER_ITEM {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
        float unit_price
        float subtotal
    }

    PRODUCT {
        int id PK
        string name
        text description
        float price
        int stock_quantity
        string sku
        datetime created_at
    }