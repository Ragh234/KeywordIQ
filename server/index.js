const express = require("express");
const cors = require("cors");
const dotenv = require("dotenv");
const connectDB = require("./config/db");

// Load env vars from project root
dotenv.config({ path: require("path").join(__dirname, "..", ".env") });

const app = express();

// Middleware
app.use(cors());
app.use(express.json({ limit: "10mb" }));

// Routes
app.use("/api/auth", require("./routes/auth"));
app.use("/api", require("./routes/reports"));

// Health check
app.get("/api/health", (req, res) => {
    res.json({ status: "ok", service: "btp-server" });
});

// Start server
const PORT = process.env.PORT || 5000;

connectDB().then(() => {
    app.listen(PORT, () => {
        console.log(`Server running on port ${PORT}`);
    });
});
