const express = require("express");
const router = express.Router();
const { signup, login, logout, getMe, updateProfile } = require("../controllers/authController");
const auth = require("../middleware/auth");

router.post("/signup", signup);
router.post("/login", login);
router.post("/logout", auth, logout);
router.get("/me", auth, getMe);
router.put("/update", auth, updateProfile);

module.exports = router;
