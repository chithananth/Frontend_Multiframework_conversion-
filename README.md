# ⚡ Multi Framework Web Code Converter

A full-stack web application that automatically converts **HTML → React JSX** and **CSS → Tailwind CSS** — with support for single files, merged output, and bulk ZIP conversion.

Built with **React + Vite** (frontend) and **Python Flask + MySQL** (backend).

---

## 🚀 Features

- 🔄 **HTML → React JSX** — Converts HTML tags, attributes, inline styles, and event handlers to valid JSX
- 🎨 **CSS → Tailwind CSS** — Maps CSS properties to Tailwind utility classes with pixel-to-unit conversion
- 📦 **ZIP Upload** — Upload multiple `.html`, `.css`, `.js`, `.jsx` files or a `.zip` and get a converted ZIP back
- 🗂️ **Conversion History** — Every conversion is saved to MySQL; view, re-download, or delete past conversions
- 📥 **Download Output** — Download converted files as `.jsx`, `.txt`, or `.zip`
- 🔔 **Toast Notifications** — Real-time success/error feedback

---
## screenshots

## Dashboard 
![Dashboard](screenshots/dashboard.png) 
## AI Response 
![AI Response](screenshots/response.png)

---

## 🖥️ Tech Stack

### Frontend
| Package | Version | Purpose |
|---|---|---|
| React.js | ^19.2.0 | UI framework |
| React Router DOM | ^7.13.0 | Client-side routing |
| Axios | ^1.13.5 | HTTP requests to Flask API |
| Lucide React | ^0.575.0 | Icons |
| react-syntax-highlighter | ^16.1.0 | Syntax-highlighted output |
| @uiw/react-textarea-code-editor | ^3.1.1 | Code input editor |
| Vite | ^7.3.1 | Build tool & dev server |

### Backend
| Package | Version | Purpose |
|---|---|---|
| Flask | 3.0.3 | Web framework & API routes |
| flask-cors | 4.0.1 | Cross-origin requests |
| flask-sqlalchemy | 3.1.1 | ORM for MySQL |
| PyMySQL | 1.1.1 | MySQL driver |
| BeautifulSoup4 | 4.12.3 | HTML parsing |
| lxml | 5.2.2 | Fast HTML/XML parser |
| cryptography | 42.0.8 | Secure DB connection |

### Database
- **MySQL** — Stores every conversion record in the `conversions` table

---

## 📁 Project Structure

```
conve/
├── backend/
│   ├── app.py                  # Flask app factory (entry point)
│   ├── config.py               # MySQL configuration
│   ├── extensions.py           # SQLAlchemy instance
│   ├── models.py               # conversions table model
│   ├── requirements.txt        # Python dependencies
│   ├── converters/
│   │   ├── html_to_react.py    # HTML → JSX conversion logic
│   │   ├── css_to_tailwind.py  # CSS → Tailwind mapping logic
│   │   └── zip_builder.py      # In-memory ZIP packaging
│   └── routes/
│       ├── convert.py          # /api/convert, /api/convert-zip, /api/download
│       └── history.py          # /api/history (GET, DELETE)
└── frontend/
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── App.jsx             # React Router setup
        ├── api/
        │   └── client.js       # Axios API functions
        └── components/
            ├── ConverterPage.jsx
            ├── OutputPanel.jsx
            ├── HistoryPage.jsx
            ├── Navbar.jsx
            ├── CodeEditor.jsx
            └── ToastProvider.jsx
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.x
- Node.js & npm
- MySQL Server

---

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/multi-framework-web-converter.git
cd multi-framework-web-converter
```

---

### 2. Backend Setup

```bash
cd conve/backend
```

**Install Python dependencies:**
```bash
pip install -r requirements.txt
```

**Create the MySQL database:**
```sql
CREATE DATABASE converter_db;
```

**Configure credentials** in `config.py` (or set environment variables):
```python
MYSQL_USER     = "root"
MYSQL_PASSWORD = "your_password"
MYSQL_HOST     = "localhost"
MYSQL_PORT     = "3306"
MYSQL_DB       = "converter_db"
```

**Start the Flask server:**
```bash
python app.py
```
> Runs on: `http://localhost:5000`  
> The `conversions` table is created automatically on first run.

---

### 3. Frontend Setup

```bash
cd conve/frontend
```

**Install dependencies:**
```bash
npm install
```

**Start the dev server:**
```bash
npm run dev
```
> Runs on: `http://localhost:5173`

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/convert` | Convert HTML or CSS code (JSON body) |
| `POST` | `/api/convert-zip` | Upload files, convert all, return ZIP |
| `GET` | `/api/download/<id>` | Download output file by conversion ID |
| `GET` | `/api/history` | Fetch last 100 conversion records |
| `DELETE` | `/api/history/<id>` | Delete a conversion record |

---

## 🗄️ Database Table

**Table name:** `conversions`

| Column | Type | Description |
|---|---|---|
| `id` | INT (PK) | Auto-increment unique ID |
| `type` | ENUM | `html_to_react` or `css_to_tailwind` |
| `input_code` | LONGTEXT | Original code submitted |
| `output_code` | LONGTEXT | Converted output code |
| `output_format` | ENUM | `single`, `merged`, or `zip` |
| `filename` | VARCHAR(255) | Output filename |
| `created_at` | DATETIME | Timestamp of conversion |

---

## 📤 Supported File Formats (ZIP Upload)

| Extension | Action |
|---|---|
| `.html` / `.htm` | Converted to React JSX component (`.jsx`) |
| `.css` | Converted to Tailwind classes (`.txt`) |
| `.js` / `.jsx` | Converted if HTML-like content detected, else passed through |
| `.zip` | Extracted and each inner file converted individually |

---

## 🧠 How It Works

### HTML → React JSX
1. BeautifulSoup4 parses the HTML into a node tree
2. Each node is recursively converted to JSX
3. HTML attributes are renamed to JSX equivalents (`class` → `className`, `for` → `htmlFor`, etc.)
4. Inline events are camelCased (`onclick` → `onClick`)
5. Inline styles are converted to JS objects (`style={{ color: 'red' }}`)
6. Self-closing void tags get `/>` syntax (`<br />`, `<img />`, etc.)
7. Multiple root elements are wrapped in a React Fragment (`<>...</>`)
8. Output is a complete functional React component with `import` and `export`

### CSS → Tailwind CSS
1. Regex splits CSS into selector + property blocks
2. Each `property: value` pair is mapped to a Tailwind class
3. Pixel values are converted using the formula: `px ÷ 4 = Tailwind unit` (e.g. `16px` → `p-4`)
4. Shorthand margin/padding is expanded to individual classes (`mt-`, `mr-`, `mb-`, `ml-`)
5. Unknown properties are preserved as CSS comments for manual review
6. Duplicate classes are removed automatically

---

## 👨‍💻 Author

**Chithanantham M**  
II MCA — Department of Computer Application  
Guide: Dr. K.R. Anathapadmanaban

---

## 📄 License

This project is for academic purposes.
