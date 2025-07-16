"use client";

import { useState, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { 
  User, 
  Bell, 
  Shield, 
  Palette, 
  Mail,
  Phone,
  MapPin,
  Briefcase,
  Save,
  Moon,
  Sun
} from "lucide-react";
import { getAvailableCurrencies, getSalaryRangeOptions } from "@/lib/currency";
import { apiService } from "@/lib/api";
import { useEffect } from "react";

export default function SettingsPage() {
  const [darkMode, setDarkMode] = useState(false);
  const [notifications, setNotifications] = useState({
    email: true,
    push: true,
    sms: false,
    jobAlerts: true,
    applicationUpdates: true,
    interviewReminders: true
  });

  const [profile, setProfile] = useState({
    firstName: "John",
    lastName: "Doe",
    email: "john.doe@example.com",
    phone: "+1 (555) 123-4567",
    location: "San Francisco, CA",
    title: "Software Engineer",
    experience: "5+ years",
    skills: "React, Node.js, Python, AWS"
  });

  const [preferences, setPreferences] = useState({
    jobTypes: ["Full-time", "Remote"],
    salaryRange: "80000-150000",
    salaryCurrency: "USD",
    locations: ["San Francisco", "New York", "Remote"],
    industries: ["Technology", "Healthcare", "Finance"]
  });

  // Load user preferences on component mount
  useEffect(() => {
    const loadPreferences = async () => {
      try {
        const userPreferences = await apiService.getUserPreferences();
        
        // Map backend preferences to frontend state
        if (userPreferences) {
          setPreferences({
            jobTypes: userPreferences.preferred_job_types || ["Full-time", "Remote"],
            salaryRange: userPreferences.salary_min && userPreferences.salary_max 
              ? `${userPreferences.salary_min}-${userPreferences.salary_max}`
              : "80000-150000",
            salaryCurrency: userPreferences.salary_currency || "USD",
            locations: userPreferences.preferred_locations || ["San Francisco", "New York", "Remote"],
            industries: userPreferences.preferred_job_titles || ["Technology", "Healthcare", "Finance"]
          });
        }
      } catch (error) {
        console.error("Failed to load preferences:", error);
      }
    };

    loadPreferences();
  }, []);

  const handleSave = async () => {
    try {
      // Save preferences to backend
      await apiService.updateUserPreferences({
        jobTypes: preferences.jobTypes,
        locations: preferences.locations,
        industries: preferences.industries,
        salaryRange: preferences.salaryRange,
        salaryCurrency: preferences.salaryCurrency
      });

      console.log("Settings saved successfully:", { profile, preferences, notifications, darkMode });
      // You could add a toast notification here
    } catch (error) {
      console.error("Failed to save preferences:", error);
      // You could add an error toast notification here
    }
  };

  return (
    <div className="space-y-8">
      <div className="bg-white rounded-xl shadow-sm px-8 py-8 mb-8 flex flex-col md:flex-row md:items-center md:justify-between border-b border-gray-100">
        <div className="mb-4 md:mb-0">
          <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight mb-2">Settings</h1>
          <p className="text-lg text-gray-500">Manage your account preferences and application settings</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Settings */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <User className="h-5 w-5" />
              <span>Profile Information</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="firstName">First Name</Label>
                <Input
                  id="firstName"
                  value={profile.firstName}
                  onChange={(e) => setProfile({...profile, firstName: e.target.value})}
                />
              </div>
              <div>
                <Label htmlFor="lastName">Last Name</Label>
                <Input
                  id="lastName"
                  value={profile.lastName}
                  onChange={(e) => setProfile({...profile, lastName: e.target.value})}
                />
              </div>
            </div>

            <div>
              <Label htmlFor="email">Email</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="email"
                  type="email"
                  value={profile.email}
                  onChange={(e) => setProfile({...profile, email: e.target.value})}
                  className="pl-10"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="phone">Phone</Label>
              <div className="relative">
                <Phone className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="phone"
                  value={profile.phone}
                  onChange={(e) => setProfile({...profile, phone: e.target.value})}
                  className="pl-10"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="location">Location</Label>
              <div className="relative">
                <MapPin className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="location"
                  value={profile.location}
                  onChange={(e) => setProfile({...profile, location: e.target.value})}
                  className="pl-10"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="title">Current Title</Label>
              <div className="relative">
                <Briefcase className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="title"
                  value={profile.title}
                  onChange={(e) => setProfile({...profile, title: e.target.value})}
                  className="pl-10"
                />
              </div>
            </div>

            <div>
              <Label htmlFor="experience">Experience Level</Label>
              <select
                id="experience"
                className="w-full p-2 border border-gray-300 rounded-md"
                value={profile.experience}
                onChange={(e) => setProfile({...profile, experience: e.target.value})}
              >
                <option value="Entry Level">Entry Level</option>
                <option value="1-2 years">1-2 years</option>
                <option value="3-5 years">3-5 years</option>
                <option value="5+ years">5+ years</option>
                <option value="10+ years">10+ years</option>
              </select>
            </div>

            <div>
              <Label htmlFor="skills">Skills</Label>
              <Input
                id="skills"
                value={profile.skills}
                onChange={(e) => setProfile({...profile, skills: e.target.value})}
                placeholder="e.g., React, Node.js, Python, AWS"
              />
            </div>
          </CardContent>
        </Card>

        {/* Quick Settings */}
        <div className="space-y-6">
          {/* Theme Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Palette className="h-5 w-5" />
                <span>Appearance</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {darkMode ? (
                    <Moon className="h-4 w-4 text-gray-600" />
                  ) : (
                    <Sun className="h-4 w-4 text-yellow-500" />
                  )}
                  <span className="text-sm font-medium">
                    {darkMode ? "Dark Mode" : "Light Mode"}
                  </span>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setDarkMode(!darkMode)}
                >
                  {darkMode ? "Light" : "Dark"}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Notifications */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Bell className="h-5 w-5" />
                <span>Notifications</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm">Email Notifications</span>
                <input
                  type="checkbox"
                  checked={notifications.email}
                  onChange={(e) => setNotifications({...notifications, email: e.target.checked})}
                  className="rounded"
                />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Push Notifications</span>
                <input
                  type="checkbox"
                  checked={notifications.push}
                  onChange={(e) => setNotifications({...notifications, push: e.target.checked})}
                  className="rounded"
                />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">SMS Notifications</span>
                <input
                  type="checkbox"
                  checked={notifications.sms}
                  onChange={(e) => setNotifications({...notifications, sms: e.target.checked})}
                  className="rounded"
                />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Job Alerts</span>
                <input
                  type="checkbox"
                  checked={notifications.jobAlerts}
                  onChange={(e) => setNotifications({...notifications, jobAlerts: e.target.checked})}
                  className="rounded"
                />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Application Updates</span>
                <input
                  type="checkbox"
                  checked={notifications.applicationUpdates}
                  onChange={(e) => setNotifications({...notifications, applicationUpdates: e.target.checked})}
                  className="rounded"
                />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Interview Reminders</span>
                <input
                  type="checkbox"
                  checked={notifications.interviewReminders}
                  onChange={(e) => setNotifications({...notifications, interviewReminders: e.target.checked})}
                  className="rounded"
                />
              </div>
            </CardContent>
          </Card>

          {/* Privacy */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="h-5 w-5" />
                <span>Privacy</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Profile Visibility</span>
                  <select className="text-sm border rounded px-2 py-1">
                    <option>Public</option>
                    <option>Private</option>
                    <option>Recruiters Only</option>
                  </select>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Data Sharing</span>
                  <input type="checkbox" className="rounded" />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Analytics</span>
                  <input type="checkbox" defaultChecked className="rounded" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Job Preferences */}
      <Card>
        <CardHeader>
          <CardTitle>Job Preferences</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="jobTypes">Preferred Job Types</Label>
              <div className="flex flex-wrap gap-2 mt-2">
                {["Full-time", "Part-time", "Contract", "Remote", "Hybrid"].map((type) => (
                  <label key={type} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={preferences.jobTypes.includes(type)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setPreferences({
                            ...preferences,
                            jobTypes: [...preferences.jobTypes, type]
                          });
                        } else {
                          setPreferences({
                            ...preferences,
                            jobTypes: preferences.jobTypes.filter(t => t !== type)
                          });
                        }
                      }}
                      className="rounded"
                    />
                    <span className="text-sm">{type}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <Label htmlFor="salaryCurrency">Currency</Label>
              <select
                id="salaryCurrency"
                className="w-full p-2 border border-gray-300 rounded-md"
                value={preferences.salaryCurrency}
                onChange={(e) => setPreferences({...preferences, salaryCurrency: e.target.value})}
              >
                {getAvailableCurrencies().map((currency) => (
                  <option key={currency.value} value={currency.value}>
                    {currency.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <Label htmlFor="salaryRange">Salary Range</Label>
              <select
                id="salaryRange"
                className="w-full p-2 border border-gray-300 rounded-md"
                value={preferences.salaryRange}
                onChange={(e) => setPreferences({...preferences, salaryRange: e.target.value})}
              >
                {getSalaryRangeOptions(preferences.salaryCurrency).map((range) => (
                  <option key={range.value} value={range.value}>
                    {range.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <Label htmlFor="locations">Preferred Locations</Label>
            <Input
              id="locations"
              value={preferences.locations.join(", ")}
              onChange={(e) => setPreferences({
                ...preferences,
                locations: e.target.value.split(", ")
              })}
              placeholder="e.g., San Francisco, New York, Remote"
            />
          </div>

          <div>
            <Label htmlFor="industries">Preferred Industries</Label>
            <Input
              id="industries"
              value={preferences.industries.join(", ")}
              onChange={(e) => setPreferences({
                ...preferences,
                industries: e.target.value.split(", ")
              })}
              placeholder="e.g., Technology, Healthcare, Finance"
            />
          </div>
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end">
        <Button onClick={handleSave} className="w-full md:w-auto">
          <Save className="mr-2 h-4 w-4" />
          Save Settings
        </Button>
      </div>
    </div>
  );
} 