import express from "express";
import multer from "multer";
import path from "path";

const app = express();
const port = 3000;

// Configure multer for file uploads
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, "uploads/");
    },
    filename: (req, file, cb) => {
        cb(null, Date.now() + path.extname(file.originalname));
    }
});

const upload = multer({ storage });

// File upload endpoint
app.post("/upload", upload.single("3dmodel"), (req, res) => {
    if (!req.file) {
        return res.status(400).send("No file was uploaded.");
    }
    res.send(`File uploaded successfully: ${req.file.filename}`);
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
// Middleware for file uploads
app.use(express.static("public"));
app.use("/uploads", express.static("uploads"));
// Route handler for file uploads\napp.post("/upload", upload.single("3dmodel"), (req, res) => {\n    if (!req.file) {\n        return res.status(400).send("No file was uploaded.");\n    }\n    res.send(`File uploaded successfully: ${req.file.filename}`);\n});
