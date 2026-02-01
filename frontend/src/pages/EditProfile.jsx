import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'
import { api } from '../api'

function EditProfile() {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const { user } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    loadExistingProfile()
  }, [])

  const loadExistingProfile = async () => {
    try {
      const result = await api.getUserProfile()
      if (result.success && result.profile) {
        setProfile(result.profile.profile_data)
        setMessage('✅ Loaded your existing profile. You can edit it anytime.')
      }
    } catch (error) {
      console.log('No existing profile found - ready to create new one')
    }
  }

  const updateProfile = (path, value) => {
    setProfile(prev => {
      const newProfile = { ...prev }
      const keys = path.split('.')
      let current = newProfile
      
      for (let i = 0; i < keys.length - 1; i++) {
        if (!current[keys[i]]) current[keys[i]] = {}
        current = current[keys[i]]
      }
      
      current[keys[keys.length - 1]] = value
      return newProfile
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-indigo-50 pt-4">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="card animate-fade-in-up">
          {/* Header Section */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-purple-500 to-indigo-600 rounded-full mb-4 shadow-lg">
              <span className="text-2xl">👤</span>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Your Persistent Profile</h1>
            <p className="text-gray-600 text-lg">
              Welcome back, <span className="font-semibold text-purple-600">{user?.email}</span>! 
              This is your single source of truth profile that will be reused across all job applications.
            </p>
          </div>

          {/* Profile Status */}
          {profile ? (
            <div className="glass-effect rounded-2xl p-6 mb-8 border border-green-200">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                    <span className="text-green-600 text-xl">✓</span>
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-green-900 mb-2">Profile Found</h3>
                  <p className="text-green-800 text-sm leading-relaxed">
                    You have an existing profile. You can edit it anytime and changes will be saved to your account.
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="glass-effect rounded-2xl p-6 mb-8 border border-amber-200">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center">
                    <span className="text-amber-600 text-xl">📝</span>
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-amber-900 mb-2">New Profile</h3>
                  <p className="text-amber-800 text-sm leading-relaxed">
                    No profile found. Upload a resume and generate a draft, or create one manually.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Complete Profile Form */}
          {profile && (
            <div className="space-y-8">
              {/* Basic Info */}
              <div className="card">
                <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center space-x-2">
                  <span>ℹ️</span>
                  <span>Basic Information</span>
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Full Name</label>
                    <input
                      type="text"
                      value={profile.basic_info?.name || ''}
                      onChange={(e) => updateProfile('basic_info.name', e.target.value)}
                      className="input-modern"
                      placeholder="Your full name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Email</label>
                    <input
                      type="email"
                      value={profile.basic_info?.email || ''}
                      onChange={(e) => updateProfile('basic_info.email', e.target.value)}
                      className="input-modern"
                      placeholder="your.email@example.com"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Phone Number</label>
                    <input
                      type="tel"
                      value={profile.basic_info?.phone || ''}
                      onChange={(e) => updateProfile('basic_info.phone', e.target.value)}
                      className="input-modern"
                      placeholder="+1 (555) 123-4567"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Location</label>
                    <input
                      type="text"
                      value={profile.basic_info?.location || ''}
                      onChange={(e) => updateProfile('basic_info.location', e.target.value)}
                      className="input-modern"
                      placeholder="City, State/Country"
                    />
                  </div>
                </div>
              </div>

              {/* Skills */}
              <div className="card">
                <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center space-x-2">
                  <span>🛠️</span>
                  <span>Skills</span>
                </h3>
                <div className="flex flex-wrap gap-2 mb-4">
                  {(profile.skill_vocab || []).map((skill, index) => (
                    <span key={index} className="badge-info flex items-center space-x-2">
                      <span>{skill}</span>
                      <button
                        onClick={() => {
                          const newSkills = [...(profile.skill_vocab || [])]
                          newSkills.splice(index, 1)
                          updateProfile('skill_vocab', newSkills)
                        }}
                        className="text-blue-600 hover:text-red-600 ml-2"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="Add a skill..."
                    className="input-modern flex-1"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && e.target.value.trim()) {
                        const newSkills = [...(profile.skill_vocab || []), e.target.value.trim()]
                        updateProfile('skill_vocab', newSkills)
                        e.target.value = ''
                      }
                    }}
                  />
                  <button
                    onClick={(e) => {
                      const input = e.target.parentElement.querySelector('input')
                      if (input.value.trim()) {
                        const newSkills = [...(profile.skill_vocab || []), input.value.trim()]
                        updateProfile('skill_vocab', newSkills)
                        input.value = ''
                      }
                    }}
                    className="btn-primary"
                  >
                    Add
                  </button>
                </div>
              </div>

              {/* Education */}
              <div className="card">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-xl font-bold text-gray-900 flex items-center space-x-2">
                    <span>🎓</span>
                    <span>Education</span>
                  </h3>
                  <button
                    onClick={() => {
                      const newEducation = [...(profile.education || []), {
                        institution: '',
                        degree: '',
                        field: '',
                        start_year: '',
                        end_year: ''
                      }]
                      updateProfile('education', newEducation)
                    }}
                    className="btn-success text-sm"
                  >
                    + Add Education
                  </button>
                </div>
                <div className="space-y-4">
                  {(profile.education || []).map((edu, index) => (
                    <div key={index} className="p-4 border border-gray-200 rounded-xl bg-gray-50">
                      <div className="flex justify-between items-start mb-4">
                        <h4 className="font-semibold text-gray-900">Education #{index + 1}</h4>
                        <button
                          onClick={() => {
                            const newEducation = [...(profile.education || [])]
                            newEducation.splice(index, 1)
                            updateProfile('education', newEducation)
                          }}
                          className="text-red-500 hover:text-red-700"
                        >
                          Remove
                        </button>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <input
                          type="text"
                          value={edu.institution || ''}
                          onChange={(e) => updateProfile(`education.${index}.institution`, e.target.value)}
                          placeholder="Institution name"
                          className="input-modern"
                        />
                        <input
                          type="text"
                          value={edu.degree || ''}
                          onChange={(e) => updateProfile(`education.${index}.degree`, e.target.value)}
                          placeholder="Degree"
                          className="input-modern"
                        />
                        <input
                          type="text"
                          value={edu.field || ''}
                          onChange={(e) => updateProfile(`education.${index}.field`, e.target.value)}
                          placeholder="Field of study"
                          className="input-modern"
                        />
                        <div className="flex gap-2">
                          <input
                            type="number"
                            value={edu.start_year || ''}
                            onChange={(e) => updateProfile(`education.${index}.start_year`, e.target.value)}
                            placeholder="Start year"
                            className="input-modern"
                          />
                          <input
                            type="number"
                            value={edu.end_year || ''}
                            onChange={(e) => updateProfile(`education.${index}.end_year`, e.target.value)}
                            placeholder="End year"
                            className="input-modern"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                  {(!profile.education || profile.education.length === 0) && (
                    <p className="text-gray-500 text-center py-4">No education entries yet. Click "Add Education" to get started.</p>
                  )}
                </div>
              </div>

              {/* Projects */}
              <div className="card">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-xl font-bold text-gray-900 flex items-center space-x-2">
                    <span>💼</span>
                    <span>Projects</span>
                  </h3>
                  <button
                    onClick={() => {
                      const newProjects = [...(profile.projects || []), {
                        name: '',
                        description: '',
                        skills: [],
                        links: ['']
                      }]
                      updateProfile('projects', newProjects)
                    }}
                    className="btn-success text-sm"
                  >
                    + Add Project
                  </button>
                </div>
                <div className="space-y-6">
                  {(profile.projects || []).map((project, index) => (
                    <div key={index} className="p-4 border border-gray-200 rounded-xl bg-gray-50">
                      <div className="flex justify-between items-start mb-4">
                        <h4 className="font-semibold text-gray-900">Project #{index + 1}</h4>
                        <button
                          onClick={() => {
                            const newProjects = [...(profile.projects || [])]
                            newProjects.splice(index, 1)
                            updateProfile('projects', newProjects)
                          }}
                          className="text-red-500 hover:text-red-700"
                        >
                          Remove
                        </button>
                      </div>
                      <div className="space-y-4">
                        <input
                          type="text"
                          value={project.name || ''}
                          onChange={(e) => updateProfile(`projects.${index}.name`, e.target.value)}
                          placeholder="Project name"
                          className="input-modern"
                        />
                        <textarea
                          value={project.description || ''}
                          onChange={(e) => updateProfile(`projects.${index}.description`, e.target.value)}
                          placeholder="Project description"
                          className="input-modern min-h-[100px]"
                        />
                        <div>
                          <label className="block text-sm font-semibold text-gray-700 mb-2">Project Links</label>
                          {(project.links || []).map((link, linkIndex) => (
                            <div key={linkIndex} className="flex gap-2 mb-2">
                              <input
                                type="url"
                                value={link || ''}
                                onChange={(e) => updateProfile(`projects.${index}.links.${linkIndex}`, e.target.value)}
                                placeholder="https://github.com/username/project"
                                className="input-modern flex-1"
                              />
                              <button
                                onClick={() => {
                                  const newLinks = [...(project.links || [])]
                                  newLinks.splice(linkIndex, 1)
                                  updateProfile(`projects.${index}.links`, newLinks)
                                }}
                                className="text-red-500 hover:text-red-700 px-3"
                              >
                                ×
                              </button>
                            </div>
                          ))}
                          <button
                            onClick={() => {
                              const newLinks = [...(project.links || []), '']
                              updateProfile(`projects.${index}.links`, newLinks)
                            }}
                            className="text-blue-600 hover:text-blue-800 text-sm"
                          >
                            + Add Link
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                  {(!profile.projects || profile.projects.length === 0) && (
                    <p className="text-gray-500 text-center py-4">No projects yet. Click "Add Project" to get started.</p>
                  )}
                </div>
              </div>

              {/* Experience/Internships */}
              <div className="card">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-xl font-bold text-gray-900 flex items-center space-x-2">
                    <span>💼</span>
                    <span>Experience</span>
                  </h3>
                  <button
                    onClick={() => {
                      const newExperience = [...(profile.internships || []), {
                        company: '',
                        role: '',
                        duration_months: '',
                        description: ''
                      }]
                      updateProfile('internships', newExperience)
                    }}
                    className="btn-success text-sm"
                  >
                    + Add Experience
                  </button>
                </div>
                <div className="space-y-4">
                  {(profile.internships || []).map((exp, index) => (
                    <div key={index} className="p-4 border border-gray-200 rounded-xl bg-gray-50">
                      <div className="flex justify-between items-start mb-4">
                        <h4 className="font-semibold text-gray-900">Experience #{index + 1}</h4>
                        <button
                          onClick={() => {
                            const newExperience = [...(profile.internships || [])]
                            newExperience.splice(index, 1)
                            updateProfile('internships', newExperience)
                          }}
                          className="text-red-500 hover:text-red-700"
                        >
                          Remove
                        </button>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <input
                          type="text"
                          value={exp.company || ''}
                          onChange={(e) => updateProfile(`internships.${index}.company`, e.target.value)}
                          placeholder="Company name"
                          className="input-modern"
                        />
                        <input
                          type="text"
                          value={exp.role || ''}
                          onChange={(e) => updateProfile(`internships.${index}.role`, e.target.value)}
                          placeholder="Role/Position"
                          className="input-modern"
                        />
                        <input
                          type="number"
                          value={exp.duration_months || ''}
                          onChange={(e) => updateProfile(`internships.${index}.duration_months`, e.target.value)}
                          placeholder="Duration (months)"
                          className="input-modern"
                        />
                      </div>
                      <textarea
                        value={exp.description || ''}
                        onChange={(e) => updateProfile(`internships.${index}.description`, e.target.value)}
                        placeholder="Description of your role and achievements"
                        className="input-modern min-h-[80px]"
                      />
                    </div>
                  ))}
                  {(!profile.internships || profile.internships.length === 0) && (
                    <p className="text-gray-500 text-center py-4">No experience entries yet. Click "Add Experience" to get started.</p>
                  )}
                </div>
              </div>

              {/* Application Constraints */}
              <div className="card">
                <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center space-x-2">
                  <span>⚙️</span>
                  <span>Application Constraints</span>
                </h3>
                <div className="mb-4 p-4 bg-blue-50 rounded-xl border border-blue-200">
                  <p className="text-blue-800 text-sm">
                    <strong>💡 Tip:</strong> These constraints help the AI autopilot system apply to jobs that match your preferences. 
                    Set your preferred locations, application limits, and companies to avoid.
                  </p>
                </div>
                <div className="space-y-6">
                  {/* Preferred Locations */}
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Preferred Locations</label>
                    <div className="flex flex-wrap gap-2 mb-3">
                      {(profile.constraints?.location || []).map((location, index) => (
                        <span key={index} className="badge-info flex items-center space-x-2">
                          <span>{location}</span>
                          <button
                            onClick={() => {
                              const newLocations = [...(profile.constraints?.location || [])]
                              newLocations.splice(index, 1)
                              updateProfile('constraints.location', newLocations)
                            }}
                            className="text-blue-600 hover:text-red-600 ml-2"
                          >
                            ×
                          </button>
                        </span>
                      ))}
                    </div>
                    <div className="flex gap-2">
                      <select
                        onChange={(e) => {
                          if (e.target.value) {
                            const currentLocations = profile.constraints?.location || []
                            if (!currentLocations.includes(e.target.value)) {
                              updateProfile('constraints.location', [...currentLocations, e.target.value])
                            }
                            e.target.value = ''
                          }
                        }}
                        className="input-modern flex-1"
                      >
                        <option value="">Select a location...</option>
                        <option value="Remote">Remote</option>
                        <option value="Hybrid">Hybrid</option>
                        <option value="On-site">On-site</option>
                        <optgroup label="United States">
                          <option value="New York, NY">New York, NY</option>
                          <option value="San Francisco, CA">San Francisco, CA</option>
                          <option value="Los Angeles, CA">Los Angeles, CA</option>
                          <option value="Seattle, WA">Seattle, WA</option>
                          <option value="Austin, TX">Austin, TX</option>
                          <option value="Chicago, IL">Chicago, IL</option>
                          <option value="Boston, MA">Boston, MA</option>
                        </optgroup>
                        <optgroup label="Canada">
                          <option value="Toronto, ON">Toronto, ON</option>
                          <option value="Vancouver, BC">Vancouver, BC</option>
                        </optgroup>
                        <optgroup label="Europe">
                          <option value="London, UK">London, UK</option>
                          <option value="Berlin, Germany">Berlin, Germany</option>
                          <option value="Amsterdam, Netherlands">Amsterdam, Netherlands</option>
                        </optgroup>
                      </select>
                      <button
                        onClick={() => {
                          const customLocation = prompt('Enter custom location:')
                          if (customLocation && customLocation.trim()) {
                            const currentLocations = profile.constraints?.location || []
                            if (!currentLocations.includes(customLocation.trim())) {
                              updateProfile('constraints.location', [...currentLocations, customLocation.trim()])
                            }
                          }
                        }}
                        className="btn-primary text-sm"
                      >
                        + Custom
                      </button>
                    </div>
                  </div>

                  {/* Job Preferences */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">Start Date (YYYY-MM)</label>
                      <input
                        type="text"
                        value={profile.constraints?.start_date || ''}
                        onChange={(e) => updateProfile('constraints.start_date', e.target.value)}
                        placeholder="2024-06"
                        className="input-modern"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">Max Applications per Day</label>
                      <input
                        type="number"
                        value={profile.constraints?.max_apps_per_day || 5}
                        onChange={(e) => updateProfile('constraints.max_apps_per_day', parseInt(e.target.value) || 5)}
                        min="1"
                        max="50"
                        className="input-modern"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">Min Match Score (0.0 - 1.0)</label>
                      <input
                        type="number"
                        value={profile.constraints?.min_match_score || 0.6}
                        onChange={(e) => updateProfile('constraints.min_match_score', parseFloat(e.target.value) || 0.6)}
                        min="0"
                        max="1"
                        step="0.1"
                        className="input-modern"
                      />
                    </div>
                    <div className="flex items-center">
                      <label className="flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={profile.constraints?.visa_required || false}
                          onChange={(e) => updateProfile('constraints.visa_required', e.target.checked)}
                          className="mr-3 w-4 h-4 text-blue-600 border-2 border-gray-300 rounded focus:ring-blue-500"
                        />
                        <span className="text-sm font-semibold text-gray-700">I require visa sponsorship</span>
                      </label>
                    </div>
                  </div>

                  {/* Blocked Companies */}
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Blocked Companies</label>
                    <div className="flex flex-wrap gap-2 mb-3">
                      {(profile.constraints?.blocked_companies || []).map((company, index) => (
                        <span key={index} className="badge-danger flex items-center space-x-2">
                          <span>{company}</span>
                          <button
                            onClick={() => {
                              const newCompanies = [...(profile.constraints?.blocked_companies || [])]
                              newCompanies.splice(index, 1)
                              updateProfile('constraints.blocked_companies', newCompanies)
                            }}
                            className="text-red-600 hover:text-red-800 ml-2"
                          >
                            ×
                          </button>
                        </span>
                      ))}
                    </div>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        placeholder="Add company to block..."
                        className="input-modern flex-1"
                        onKeyPress={(e) => {
                          if (e.key === 'Enter' && e.target.value.trim()) {
                            const currentCompanies = profile.constraints?.blocked_companies || []
                            if (!currentCompanies.includes(e.target.value.trim())) {
                              updateProfile('constraints.blocked_companies', [...currentCompanies, e.target.value.trim()])
                            }
                            e.target.value = ''
                          }
                        }}
                      />
                      <button
                        onClick={(e) => {
                          const input = e.target.parentElement.querySelector('input')
                          if (input.value.trim()) {
                            const currentCompanies = profile.constraints?.blocked_companies || []
                            if (!currentCompanies.includes(input.value.trim())) {
                              updateProfile('constraints.blocked_companies', [...currentCompanies, input.value.trim()])
                            }
                            input.value = ''
                          }
                        }}
                        className="btn-danger text-sm"
                      >
                        Block
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap justify-center gap-4 mb-8 animate-fade-in-up">
                <button
                  onClick={async () => {
                    setLoading(true)
                    try {
                      const result = await api.saveProfile(user.id, profile)
                      if (result.success) {
                        setMessage('✅ Profile saved successfully!')
                      } else {
                        setMessage('❌ Failed to save profile')
                      }
                    } catch (error) {
                      setMessage(`❌ Error: ${error.response?.data?.detail || error.message}`)
                    } finally {
                      setLoading(false)
                    }
                  }}
                  disabled={loading}
                  className={`btn-success ${loading ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105'} transition-all duration-300`}
                >
                  {loading ? (
                    <span className="flex items-center space-x-2">
                      <div className="spinner"></div>
                      <span>Saving...</span>
                    </span>
                  ) : (
                    <span className="flex items-center space-x-2">
                      <span>💾</span>
                      <span>Save Profile</span>
                    </span>
                  )}
                </button>

                <button
                  onClick={() => navigate('/jobs')}
                  className="btn-primary hover:scale-105 transition-all duration-300"
                >
                  <span className="flex items-center space-x-2">
                    <span>💼</span>
                    <span>Browse Jobs</span>
                  </span>
                </button>

                <button
                  onClick={() => navigate('/dashboard')}
                  className="btn-secondary hover:scale-105 transition-all duration-300"
                >
                  <span className="flex items-center space-x-2">
                    <span>📊</span>
                    <span>View Dashboard</span>
                  </span>
                </button>

                <button
                  onClick={async () => {
                    const resumeText = localStorage.getItem('resumeText')
                    if (resumeText) {
                      setLoading(true)
                      try {
                        const result = await api.generateDraftProfile(resumeText, user.id)
                        if (result.success) {
                          setProfile(result.draft_profile)
                          setMessage('✅ Profile regenerated from your resume!')
                        } else {
                          setMessage('❌ Failed to regenerate profile')
                        }
                      } catch (error) {
                        setMessage(`❌ Error: ${error.response?.data?.detail || error.message}`)
                      } finally {
                        setLoading(false)
                      }
                    } else {
                      setMessage('❌ Please upload a resume first')
                    }
                  }}
                  disabled={loading || !localStorage.getItem('resumeText')}
                  className={`bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-xl font-semibold shadow-lg transform transition-all duration-300 hover:scale-105 hover:shadow-xl ${loading || !localStorage.getItem('resumeText') ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <span className="flex items-center space-x-2">
                    <span>🔄</span>
                    <span>Regenerate from Resume</span>
                  </span>
                </button>
              </div>
            </div>
          )}

          {/* No Profile State */}
          {!profile && (
            <div className="text-center py-12">
              <div className="glass-effect rounded-2xl p-8 border border-blue-200">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-blue-600 text-2xl">📄</span>
                </div>
                <p className="text-gray-600 mb-6 text-lg">
                  No profile found. Please upload a resume first to generate your profile.
                </p>
                <div className="flex flex-wrap justify-center gap-4">
                  <button
                    onClick={() => navigate('/upload-resume')}
                    className="btn-primary"
                  >
                    <span className="flex items-center space-x-2">
                      <span>📤</span>
                      <span>Upload Resume</span>
                    </span>
                  </button>
                  <button
                    onClick={async () => {
                      const resumeText = localStorage.getItem('resumeText')
                      if (resumeText) {
                        setLoading(true)
                        try {
                          const result = await api.generateDraftProfile(resumeText, user.id)
                          if (result.success) {
                            setProfile(result.draft_profile)
                            setMessage('✅ Draft profile generated from your resume!')
                          } else {
                            setMessage('❌ Failed to generate profile')
                          }
                        } catch (error) {
                          setMessage(`❌ Error: ${error.response?.data?.detail || error.message}`)
                        } finally {
                          setLoading(false)
                        }
                      } else {
                        setMessage('❌ Please upload a resume first')
                      }
                    }}
                    disabled={loading || !localStorage.getItem('resumeText')}
                    className={`btn-success ${loading || !localStorage.getItem('resumeText') ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    <span className="flex items-center space-x-2">
                      <span>🤖</span>
                      <span>Generate from Resume</span>
                    </span>
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Messages */}
          {message && (
            <div className={`p-4 rounded-xl animate-fade-in-up mt-6 ${
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

          {/* Safety Notice */}
          <div className="mt-8 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-6 border border-blue-200">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-blue-600 text-xl">🔒</span>
                </div>
              </div>
              <div>
                <h4 className="text-lg font-semibold text-blue-900 mb-3">Persistent Profile Benefits</h4>
                <ul className="space-y-2 text-blue-800 text-sm">
                  <li className="flex items-start space-x-2">
                    <span className="text-blue-600 mt-0.5">•</span>
                    <span>Your profile is saved securely to your account</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-blue-600 mt-0.5">•</span>
                    <span>Edit anytime - changes are automatically saved</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-blue-600 mt-0.5">•</span>
                    <span>Reused across all job applications for consistency</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-blue-600 mt-0.5">•</span>
                    <span>Single source of truth for all your information</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-blue-600 mt-0.5">•</span>
                    <span>AI assists but you maintain complete control</span>
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

export default EditProfile