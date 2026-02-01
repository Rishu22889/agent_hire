import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'
import { api } from '../api'

function UploadResume() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [extractedText, setExtractedText] = useState('')
  const [resumeHash, setResumeHash] = useState('')
  const [showExtractedText, setShowExtractedText] = useState(false)
  const { user } = useAuth()
  const navigate = useNavigate()

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
    setMessage('')
    setExtractedText('')
    setResumeHash('')
  }

  const handleUpload = async () => {
    if (!file) {
      setMessage('Please select a resume file')
      return
    }

    setLoading(true)
    try {
      // Upload resume and extract text (pdfplumber ONLY for PDFs)
      const result = await api.uploadResume(file)
      
      if (result.success) {
        setExtractedText(result.extracted_text)
        setResumeHash(result.resume_hash)
        
        // Store for next steps (temporary - will be replaced by persistent profile)
        localStorage.setItem('resumeHash', result.resume_hash)
        localStorage.setItem('resumeText', result.extracted_text)
        
        setMessage(`✅ Resume uploaded and text extracted successfully. Ready for profile generation.`)
      } else {
        setMessage(`❌ Upload failed`)
      }
    } catch (error) {
      setMessage(`❌ Error: ${error.response?.data?.detail || error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const proceedToProfileGeneration = () => {
    if (resumeHash && extractedText) {
      navigate('/profile')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 pt-4">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="card animate-fade-in-up">
          {/* Header Section */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full mb-4 shadow-lg">
              <span className="text-2xl">📄</span>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Your Resume</h1>
            <p className="text-gray-600 text-lg">
              Welcome back, <span className="font-semibold text-indigo-600">{user?.email}</span>! 
              Upload your resume to create or update your persistent profile.
            </p>
          </div>

          {/* Info Card */}
          <div className="glass-effect rounded-2xl p-6 mb-8 border border-blue-200">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-blue-600 text-xl">📋</span>
                </div>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-blue-900 mb-2">Persistent Profile</h3>
                <p className="text-blue-800 text-sm leading-relaxed">
                  Your profile will be saved to your account and reused across all job applications. 
                  You can edit it anytime and it will be your single source of truth.
                </p>
              </div>
            </div>
          </div>

          {/* Upload Section */}
          <div className="relative">
            <div className="border-2 border-dashed border-gray-300 hover:border-indigo-400 transition-colors duration-300 rounded-2xl p-12 text-center bg-gradient-to-br from-gray-50 to-indigo-50 hover:from-indigo-50 hover:to-purple-50">
              <div className="space-y-6">
                <div className="mx-auto w-20 h-20 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg">
                  <span className="text-3xl">⬆️</span>
                </div>
                
                <div>
                  <input
                    type="file"
                    accept=".pdf,.doc,.docx,.txt"
                    onChange={handleFileChange}
                    className="hidden"
                    id="resume-upload"
                  />
                  <label
                    htmlFor="resume-upload"
                    className="btn-primary cursor-pointer inline-block"
                  >
                    Choose Resume File
                  </label>
                </div>
                
                <div className="text-sm text-gray-600">
                  <p className="font-medium mb-2">Supported formats:</p>
                  <div className="flex justify-center space-x-4">
                    <span className="badge-info">PDF (recommended)</span>
                    <span className="badge-info">Word (.doc, .docx)</span>
                    <span className="badge-info">Text (.txt)</span>
                  </div>
                </div>
                
                {file && (
                  <div className="animate-fade-in-up">
                    <div className="bg-white rounded-xl p-4 shadow-soft border border-blue-200">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                          <span className="text-blue-600">📎</span>
                        </div>
                        <div className="flex-1 text-left">
                          <p className="font-semibold text-gray-900">{file.name}</p>
                          <p className="text-sm text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
                        </div>
                        <div className="text-green-500">
                          <span className="text-xl">✓</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                <button
                  onClick={handleUpload}
                  disabled={loading || !file}
                  className={`btn-primary ${loading || !file ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105'} transition-all duration-300`}
                >
                  {loading ? (
                    <span className="flex items-center space-x-2">
                      <div className="spinner"></div>
                      <span>Processing Resume...</span>
                    </span>
                  ) : (
                    <span className="flex items-center space-x-2">
                      <span>🚀</span>
                      <span>Upload & Extract Text</span>
                    </span>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Extracted Text Section */}
          {extractedText && (
            <div className="animate-slide-in-right mt-8">
              <div className="card-gradient">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-xl font-bold text-white flex items-center space-x-2">
                    <span>📝</span>
                    <span>Extracted Text</span>
                  </h3>
                  <button
                    onClick={() => setShowExtractedText(!showExtractedText)}
                    className="bg-white bg-opacity-20 hover:bg-opacity-30 text-white px-4 py-2 rounded-xl transition-all duration-300 transform hover:scale-105"
                  >
                    {showExtractedText ? '👁️ Hide' : '👁️ Show'} Text
                  </button>
                </div>
                
                {showExtractedText && (
                  <div className="bg-white bg-opacity-10 rounded-xl p-4 backdrop-blur-sm border border-white border-opacity-20">
                    <div className="max-h-80 overflow-y-auto">
                      <pre className="text-white text-sm whitespace-pre-wrap font-mono leading-relaxed">
                        {extractedText}
                      </pre>
                    </div>
                  </div>
                )}
                
                <div className="mt-6 bg-green-100 bg-opacity-20 rounded-xl p-4 border border-green-300 border-opacity-30">
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0">
                      <span className="text-green-200 text-xl">✓</span>
                    </div>
                    <div>
                      <p className="text-green-100 text-sm leading-relaxed">
                        <span className="font-semibold">Text extraction complete!</span> This raw text will be used to generate your draft profile. 
                        No AI processing has been applied yet - you'll review everything in the next step.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Next Step Button */}
          {resumeHash && extractedText && (
            <div className="text-center mt-8 animate-fade-in-up">
              <button
                onClick={proceedToProfileGeneration}
                className="btn-success text-lg px-8 py-4 shadow-large"
              >
                <span className="flex items-center space-x-3">
                  <span>🎯</span>
                  <span>Continue to Profile Generation</span>
                  <span>→</span>
                </span>
              </button>
            </div>
          )}

          {/* Messages */}
          {message && (
            <div className={`mt-6 p-4 rounded-xl animate-fade-in-up ${
              message.includes('✅') 
                ? 'bg-green-50 border border-green-200 text-green-800' 
                : 'bg-red-50 border border-red-200 text-red-800'
            }`}>
              <div className="flex items-start space-x-3">
                <span className="text-xl">
                  {message.includes('✅') ? '✅' : '❌'}
                </span>
                <p className="flex-1 font-medium">{message}</p>
              </div>
            </div>
          )}

          {/* Process Overview */}
          <div className="mt-8 glass-effect rounded-2xl p-6 border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
              <span>🗺️</span>
              <span>Your Persistent Profile Journey</span>
            </h3>
            <div className="space-y-3">
              {[
                { step: 1, text: 'Upload resume & extract text', completed: !!resumeHash },
                { step: 2, text: 'AI generates draft profile (you review everything)', completed: false },
                { step: 3, text: 'Edit and verify your persistent profile', completed: false },
                { step: 4, text: 'Browse job listings and select opportunities', completed: false },
                { step: 5, text: 'Run autonomous applications on selected jobs', completed: false },
                { step: 6, text: 'Monitor results and manage application history', completed: false }
              ].map(({ step, text, completed }) => (
                <div key={step} className="flex items-center space-x-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                    completed 
                      ? 'bg-green-500 text-white' 
                      : 'bg-gray-200 text-gray-600'
                  }`}>
                    {completed ? '✓' : step}
                  </div>
                  <span className={`${completed ? 'text-green-700 font-semibold' : 'text-gray-600'}`}>
                    {text}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Safety Notice */}
          <div className="mt-8 bg-gradient-to-r from-amber-50 to-orange-50 rounded-2xl p-6 border border-amber-200">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center">
                  <span className="text-amber-600 text-xl">🔒</span>
                </div>
              </div>
              <div>
                <h4 className="text-lg font-semibold text-amber-900 mb-3">Your Data is Safe</h4>
                <ul className="space-y-2 text-amber-800 text-sm">
                  <li className="flex items-start space-x-2">
                    <span className="text-amber-600 mt-0.5">•</span>
                    <span>We only extract text from your resume - no AI analysis yet</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-amber-600 mt-0.5">•</span>
                    <span>Your profile is saved securely to your account</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-amber-600 mt-0.5">•</span>
                    <span>You'll review and edit everything before any applications are sent</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-amber-600 mt-0.5">•</span>
                    <span>The system never invents or guesses information</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-amber-600 mt-0.5">•</span>
                    <span>You maintain complete control throughout the process</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default UploadResume