import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import api from "../utils/api";
import Input from "../components/ui/Input";
import Button from "../components/ui/Button";
import { CheckCircle, AlertCircle } from "lucide-react";

export default function Settings() {
    const { user, updateUser } = useAuth();
    const [name, setName] = useState(user?.name || "");
    const [currentPassword, setCurrentPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleUpdateName = async (e) => {
        e.preventDefault();
        setMessage("");
        setError("");
        setLoading(true);
        try {
            const res = await api.put("/auth/update", { name: name.trim() });
            updateUser(res.data.user);
            setMessage("Name updated successfully");
        } catch (err) {
            setError(err.response?.data?.message || "Update failed");
        } finally {
            setLoading(false);
        }
    };

    const handleChangePassword = async (e) => {
        e.preventDefault();
        if (!currentPassword || !newPassword) return;
        if (newPassword.length < 6) {
            setError("New password must be at least 6 characters");
            return;
        }
        setMessage("");
        setError("");
        setLoading(true);
        try {
            await api.put("/auth/update", { currentPassword, newPassword });
            setCurrentPassword("");
            setNewPassword("");
            setMessage("Password changed successfully");
        } catch (err) {
            setError(err.response?.data?.message || "Password change failed");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-lg mx-auto space-y-6 animate-fade-in">
            <h2
                className="text-lg font-bold text-white"
                style={{ fontFamily: "Poppins, sans-serif" }}
            >
                Settings
            </h2>

            {message && (
                <div className="flex items-center gap-2 p-3 text-sm text-emerald-300 bg-emerald-500/10 border border-emerald-500/20 rounded-xl animate-fade-in">
                    <CheckCircle className="w-4 h-4 shrink-0" />
                    {message}
                </div>
            )}
            {error && (
                <div className="flex items-center gap-2 p-3 text-sm text-red-300 bg-red-500/10 border border-red-500/20 rounded-xl animate-fade-in">
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    {error}
                </div>
            )}

            {/* Profile */}
            <div className="glass-card p-5">
                <h3 className="text-sm font-semibold text-white mb-4">
                    Profile
                </h3>
                <form onSubmit={handleUpdateName} className="space-y-4">
                    <div>
                        <label className="block text-xs text-slate-400 mb-1.5">
                            Email
                        </label>
                        <input
                            type="email"
                            value={user?.email || ""}
                            disabled
                            className="w-full px-4 py-3 bg-white/[0.03] border border-white/[0.06] rounded-xl text-slate-500 text-sm cursor-not-allowed"
                        />
                    </div>
                    <Input
                        id="settings-name"
                        label="Name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                    />
                    <Button
                        type="submit"
                        loading={loading}
                        disabled={!name.trim() || name.trim() === user?.name}
                        className="!w-auto"
                    >
                        Save Changes
                    </Button>
                </form>
            </div>

            {/* Change Password */}
            <div className="glass-card p-5">
                <h3 className="text-sm font-semibold text-white mb-4">
                    Change Password
                </h3>
                <form onSubmit={handleChangePassword} className="space-y-4">
                    <Input
                        id="settings-current-password"
                        label="Current Password"
                        type="password"
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                        autoComplete="current-password"
                    />
                    <Input
                        id="settings-new-password"
                        label="New Password"
                        type="password"
                        placeholder="Min 6 characters"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        autoComplete="new-password"
                    />
                    <Button
                        type="submit"
                        loading={loading}
                        disabled={!currentPassword || !newPassword}
                        className="!w-auto"
                    >
                        Change Password
                    </Button>
                </form>
            </div>
        </div>
    );
}
