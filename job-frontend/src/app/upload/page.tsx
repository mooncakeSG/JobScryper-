"use client";

import { useState, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { 
  Upload, 
  File, 
  CheckCircle, 
  AlertCircle, 
  FileText,
  Loader2
} from "lucide-react";
import { apiService, ResumeAnalysis } from "@/lib/api";
import { activityService } from "@/lib/activity";



export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [analysis, setAnalysis] = useState<ResumeAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === "application/pdf" || 
          droppedFile.type === "application/vnd.openxmlformats-officedocument.wordprocessingml.document") {
        setFile(droppedFile);
        setError(null);
      } else {
        setError("Please upload a PDF or DOCX file");
      }
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type === "application/pdf" || 
          selectedFile.type === "application/vnd.openxmlformats-officedocument.wordprocessingml.document") {
        setFile(selectedFile);
        setError(null);
      } else {
        setError("Please upload a PDF or DOCX file");
      }
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      const result = await apiService.analyzeResume(file);
      
      if (result.success && result.data) {
        setAnalysis(result.data);
        
        // Log activity
        try {
          await activityService.logResumeUploaded();
        } catch (activityError) {
          console.error('Error logging activity:', activityError);
        }
      } else {
        setError(result.error || "Failed to analyze resume. Please try again.");
      }
    } catch (err) {
      setError("Failed to analyze resume. Please try again.");
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return "Excellent";
    if (score >= 60) return "Good";
    return "Needs Improvement";
  };

  return (
    <div className="space-y-8">
      <div className="bg-white rounded-xl shadow-sm px-8 py-8 mb-8 flex flex-col md:flex-row md:items-center md:justify-between border-b border-gray-100">
        <div className="mb-4 md:mb-0">
          <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight mb-2">Upload Your Resume</h1>
          <p className="text-lg text-gray-500">Upload your resume for AI-powered ATS analysis and optimization suggestions</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Upload Section */}
        <Card className="rounded-2xl shadow-sm border border-gray-100 bg-white">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-xl font-bold">
              <Upload className="h-6 w-6" />
              <span>Upload Resume</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Drag and Drop Area */}
            <div
              className={`border-2 border-dashed rounded-xl p-10 text-center transition-colors cursor-pointer select-none focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                dragActive 
                  ? "border-blue-500 bg-blue-50" 
                  : "border-gray-300 hover:border-blue-400"
              }`}
              tabIndex={0}
              aria-label="Drop your resume here or click to browse files"
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => document.getElementById('resume-upload')?.click()}
            >
              <Upload className="mx-auto h-14 w-14 text-gray-300 mb-4" />
              <p className="text-xl font-semibold text-gray-900 mb-2">Drop your resume here</p>
              <p className="text-base text-gray-500 mb-4">or click to browse files</p>
              <Label htmlFor="resume-upload" className="cursor-pointer">
                <Input
                  id="resume-upload"
                  type="file"
                  accept=".pdf,.docx"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <Button variant="outline" className="w-full sm:w-auto font-semibold">
                  Choose File
                </Button>
              </Label>
            </div>

            {/* File Info */}
            {file && (
              <div className="flex items-center space-x-3 p-4 bg-blue-50 rounded-lg border border-blue-100">
                <FileText className="h-6 w-6 text-blue-600" />
                <div className="flex-1 min-w-0">
                  <p className="text-base font-medium text-gray-900 truncate">{file.name}</p>
                  <p className="text-xs text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="flex items-center space-x-2 p-4 bg-red-50 rounded-lg border border-red-200">
                <AlertCircle className="h-6 w-6 text-red-600" />
                <p className="text-base text-red-700 font-medium">{error}</p>
              </div>
            )}

            {/* Upload Button */}
            <Button
              onClick={handleUpload}
              disabled={!file || uploading}
              className="w-full h-12 text-lg font-semibold shadow-md"
            >
              {uploading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-5 w-5" />
                  Analyze Resume
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Analysis Results */}
        <Card className="rounded-2xl shadow-sm border border-gray-100 bg-white">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-xl font-bold text-black">
              <FileText className="h-6 w-6" />
              <span>ATS Analysis Results</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {analysis ? (
              <div className="space-y-6">
                {/* ATS Score */}
                <div className="text-center mb-6">
                  <div className={`text-5xl font-extrabold ${getScoreColor(analysis.ats_score)}`}>{analysis.ats_score}%</div>
                  <p className="text-base text-gray-700 mt-1 font-semibold">{getScoreLabel(analysis.ats_score)}</p>
                </div>

                {/* Strengths */}
                {analysis.strengths && analysis.strengths.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-green-700 mb-2 text-base">Strengths</h3>
                    <ul className="space-y-2">
                      {analysis.strengths.map((strength, index) => (
                        <li key={index} className="text-sm text-gray-800 flex items-start bg-green-50 rounded-lg px-3 py-2">
                          <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                          {strength}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Suggestions */}
                {analysis.suggestions && analysis.suggestions.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-blue-700 mb-2 text-base">Suggestions</h3>
                    <ul className="space-y-2">
                      {analysis.suggestions.map((suggestion, index) => (
                        <li key={index} className="text-sm text-gray-800 flex items-start bg-blue-50 rounded-lg px-3 py-2">
                          <AlertCircle className="h-4 w-4 text-blue-500 mr-2 mt-0.5 flex-shrink-0" />
                          {suggestion}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Keywords */}
                {analysis.keywords && analysis.keywords.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-purple-700 mb-2 text-base">Key Skills Found</h3>
                    <div className="flex flex-wrap gap-2">
                      {analysis.keywords.map((keyword, index) => (
                        <span
                          key={index}
                          className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-semibold shadow-sm"
                        >
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <FileText className="mx-auto h-14 w-14 text-gray-300 mb-4" />
                <p className="text-lg text-gray-500 font-medium">Upload your resume to see ATS analysis results</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 