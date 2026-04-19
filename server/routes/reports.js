const express = require("express");
const router = express.Router();
const {
    analyze,
    saveReport,
    getReports,
    getReport,
    deleteReport,
} = require("../controllers/keywordController");
const auth = require("../middleware/auth");

// All routes require authentication
router.post("/keyword/analyze", auth, analyze);
router.post("/reports", auth, saveReport);
router.get("/reports", auth, getReports);
router.get("/reports/:id", auth, getReport);
router.delete("/reports/:id", auth, deleteReport);

module.exports = router;
