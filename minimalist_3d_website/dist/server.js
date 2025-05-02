"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const multer_1 = __importDefault(require("multer"));
const path_1 = __importDefault(require("path"));
const app = (0, express_1.default)();
const port = 3000;
// Configure multer for file uploads
const storage = multer_1.default.diskStorage({
    destination: (req, file, cb) => {
        cb(null, "uploads/");
    },
    filename: (req, file, cb) => {
        cb(null, Date.now() + path_1.default.extname(file.originalname));
    }
});
const upload = (0, multer_1.default)({ storage });
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
app.use(express_1.default.static("public"));
app.use("/uploads", express_1.default.static("uploads"));
// Route handler for file uploads\napp.post("/upload", upload.single("3dmodel"), (req, res) => {\n    if (!req.file) {\n        return res.status(400).send("No file was uploaded.");\n    }\n    res.send(`File uploaded successfully: ${req.file.filename}`);\n});
