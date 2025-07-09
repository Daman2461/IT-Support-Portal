# IT Support Portal

A comprehensive IT support ticket management system built with Flask. This application allows users to create and track support tickets, while providing IT staff with tools to manage and resolve issues efficiently.

## Features

- User authentication and role-based access control
- Ticket creation and management
- Real-time ticket status updates
- Priority-based ticket categorization
- Email notifications
- Comment system for ticket discussions
- Responsive web interface

## Prerequisites

- Python 3.7+
- pip (Python package manager)
- SMTP server access (for email notifications)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd it-support-portal
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
```
SECRET_KEY=your-secret-key-here
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your web browser and navigate to `http://localhost:5000`

3. Log in with your credentials (default admin account will be created on first run)

## Project Structure

```
it-support-portal/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   ├── dashboard.html  # Main dashboard template
│   ├── new_ticket.html # New ticket form
│   └── view_ticket.html # Ticket details view
└── README.md          # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 