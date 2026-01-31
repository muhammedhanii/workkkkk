'use client'

import { useState } from 'react'
import Image from 'next/image'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

interface Board {
  board_number: number
  length: number
  width: number
  pieces: Array<{
    name: string
    length: number
    width: number
    x: number
    y: number
    rotated: boolean
  }>
  utilization: number
  waste_area: number
}

interface CuttingResult {
  boards: Board[]
  total_boards: number
  overall_utilization: number
  rejected_pieces: any[]
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<CuttingResult | null>(null)
  const [reportUrl, setReportUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setError(null)
      setResult(null)
      setReportUrl(null)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) {
      setError('Please select an Excel file')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)
    setReportUrl(null)

    try {
      // First, get the calculation results
      const formData = new FormData()
      formData.append('file', file)

      const calcResponse = await fetch(`${API_URL}/calculate`, {
        method: 'POST',
        body: formData,
      })

      if (!calcResponse.ok) {
        const errorData = await calcResponse.json()
        throw new Error(errorData.detail || 'Calculation failed')
      }

      const calcData = await calcResponse.json()
      setResult(calcData.result)

      // Then, get the report image
      const reportFormData = new FormData()
      reportFormData.append('file', file)

      const reportResponse = await fetch(`${API_URL}/calculate/report`, {
        method: 'POST',
        body: reportFormData,
      })

      if (!reportResponse.ok) {
        throw new Error('Report generation failed')
      }

      const blob = await reportResponse.blob()
      const url = URL.createObjectURL(blob)
      setReportUrl(url)

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const downloadReport = () => {
    if (reportUrl) {
      const a = document.createElement('a')
      a.href = reportUrl
      a.download = 'cutting_report.png'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
    }
  }

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            Wood Cutting Optimizer
          </h1>
          <p className="text-gray-600">
            Professional AutoCUT-style cutting optimization for wood boards
          </p>
        </div>

        {/* Upload Form */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-semibold mb-4 text-gray-800">
            Upload Excel File
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors">
              <input
                type="file"
                accept=".xlsx,.xls"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer inline-flex items-center gap-2"
              >
                <svg
                  className="w-12 h-12 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
                <div>
                  <p className="text-lg text-gray-700">
                    {file ? file.name : 'Click to select Excel file'}
                  </p>
                  <p className="text-sm text-gray-500">
                    .xlsx or .xls format
                  </p>
                </div>
              </label>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={!file || loading}
              className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Processing...' : 'Calculate Cutting Layout'}
            </button>
          </form>
        </div>

        {/* Results */}
        {result && (
          <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
            <h2 className="text-2xl font-semibold mb-4 text-gray-800">
              Results
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Total Boards</p>
                <p className="text-3xl font-bold text-blue-600">
                  {result.total_boards}
                </p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Utilization</p>
                <p className="text-3xl font-bold text-green-600">
                  {result.overall_utilization.toFixed(2)}%
                </p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Board Size</p>
                <p className="text-xl font-bold text-purple-600">
                  240 × 120 cm
                </p>
              </div>
            </div>

            {reportUrl && (
              <div className="space-y-4">
                <button
                  onClick={downloadReport}
                  className="bg-green-600 text-white py-2 px-6 rounded-lg font-semibold hover:bg-green-700 transition-colors"
                >
                  Download Report (PNG)
                </button>

                <div className="border border-gray-200 rounded-lg overflow-hidden">
                  <img
                    src={reportUrl}
                    alt="Cutting Report"
                    className="w-full"
                  />
                </div>
              </div>
            )}
          </div>
        )}

        {/* Instructions */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-semibold mb-4 text-gray-800">
            Excel File Format
          </h2>
          <p className="text-gray-600 mb-4">
            Your Excel file should contain the following columns:
          </p>
          <ul className="space-y-2 text-gray-700">
            <li className="flex items-start">
              <span className="font-semibold mr-2">•</span>
              <span><strong>الاسم</strong> - Part name (text)</span>
            </li>
            <li className="flex items-start">
              <span className="font-semibold mr-2">•</span>
              <span><strong>الطول</strong> - Length in cm (number)</span>
            </li>
            <li className="flex items-start">
              <span className="font-semibold mr-2">•</span>
              <span><strong>العرض</strong> - Width in cm (number)</span>
            </li>
            <li className="flex items-start">
              <span className="font-semibold mr-2">•</span>
              <span><strong>الكمية</strong> - Quantity (number)</span>
            </li>
            <li className="flex items-start">
              <span className="font-semibold mr-2">•</span>
              <span><strong>شرط طول</strong> - Length constraint (boolean)</span>
            </li>
            <li className="flex items-start">
              <span className="font-semibold mr-2">•</span>
              <span><strong>شرط عرض</strong> - Width constraint (boolean)</span>
            </li>
          </ul>
        </div>
      </div>
    </main>
  )
}
