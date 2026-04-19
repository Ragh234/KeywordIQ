const axios = require("axios");
const Report = require("../models/Report");

const PYTHON_API = process.env.PYTHON_API_URL || "http://127.0.0.1:8000";

// POST /api/keyword/analyze
exports.analyze = async (req, res) => {
    try {
        const { keyword, max_pages, top_n } = req.body;

        if (!keyword || !keyword.trim()) {
            return res.status(400).json({ message: "Keyword is required" });
        }

        // Proxy to Python FastAPI analysis service
        const response = await axios.post(`${PYTHON_API}/api/analyze`, {
            keyword: keyword.trim(),
            max_pages: max_pages || 1,
            top_n: top_n || 20,
        });

        res.json(response.data);
    } catch (error) {
        console.error("Analysis error:", error.message);
        if (error.response) {
            return res.status(error.response.status).json({
                message: error.response.data?.detail || "Analysis failed",
            });
        }
        res.status(500).json({ message: "Analysis service unavailable" });
    }
};

// POST /api/reports (save a report)
exports.saveReport = async (req, res) => {
    try {
        const { keyword, results } = req.body;

        if (!keyword || !results) {
            return res.status(400).json({ message: "Keyword and results are required" });
        }

        const report = await Report.create({
            userId: req.user._id,
            keyword,
            results,
        });

        res.status(201).json(report);
    } catch (error) {
        console.error("Save report error:", error);
        res.status(500).json({ message: "Server error" });
    }
};

// GET /api/reports
exports.getReports = async (req, res) => {
    try {
        const reports = await Report.find({ userId: req.user._id })
            .sort({ createdAt: -1 })
            .select("keyword createdAt results.total_products results.search_keyword");

        // Build summary for each report
        const summaries = reports.map((r) => ({
            _id: r._id,
            keyword: r.keyword,
            createdAt: r.createdAt,
            totalProducts: r.results?.total_products || 0,
        }));

        res.json(summaries);
    } catch (error) {
        console.error("Get reports error:", error);
        res.status(500).json({ message: "Server error" });
    }
};

// GET /api/reports/:id
exports.getReport = async (req, res) => {
    try {
        const report = await Report.findOne({
            _id: req.params.id,
            userId: req.user._id,
        });

        if (!report) {
            return res.status(404).json({ message: "Report not found" });
        }

        res.json(report);
    } catch (error) {
        console.error("Get report error:", error);
        res.status(500).json({ message: "Server error" });
    }
};

// DELETE /api/reports/:id
exports.deleteReport = async (req, res) => {
    try {
        const report = await Report.findOneAndDelete({
            _id: req.params.id,
            userId: req.user._id,
        });

        if (!report) {
            return res.status(404).json({ message: "Report not found" });
        }

        res.json({ message: "Report deleted" });
    } catch (error) {
        console.error("Delete report error:", error);
        res.status(500).json({ message: "Server error" });
    }
};
