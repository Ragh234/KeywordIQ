const mongoose = require("mongoose");

const reportSchema = new mongoose.Schema(
    {
        userId: {
            type: mongoose.Schema.Types.ObjectId,
            ref: "User",
            required: true,
        },
        keyword: {
            type: String,
            required: true,
            trim: true,
        },
        results: {
            type: mongoose.Schema.Types.Mixed,
            required: true,
        },
    },
    { timestamps: true }
);

// Index for fast user-specific queries
reportSchema.index({ userId: 1, createdAt: -1 });

module.exports = mongoose.model("Report", reportSchema);
