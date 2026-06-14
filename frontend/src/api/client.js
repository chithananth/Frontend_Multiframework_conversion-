import axios from 'axios'

const api = axios.create({
    baseURL: '/api',
    timeout: 30000,
})

/**
 * Convert code.
 * @param {object} payload - { type, input_code, output_format, component_name }
 * @returns Axios response
 */
export async function convertCode(payload) {
    return api.post('/convert', payload)
}

/**
 * Fetch conversion history.
 */
export async function fetchHistory() {
    return api.get('/history')
}

/**
 * Delete a history record.
 */
export async function deleteHistory(id) {
    return api.delete(`/history/${id}`)
}

/**
 * Download a file by conversion ID.
 * Triggers a browser download.
 */
export async function downloadFile(id, filename) {
    const response = await api.get(`/download/${id}`, { responseType: 'blob' })
    const url = URL.createObjectURL(new Blob([response.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = filename || `output_${id}.txt`
    a.click()
    URL.revokeObjectURL(url)
}

/**
 * Download a ZIP: POSTing to /convert with output_format=zip
 * This gets handled by convertCode, but re-download from history needs blob GET.
 */
export async function downloadZip(id, filename) {
    const response = await api.get(`/download/${id}`, { responseType: 'blob' })
    const url = URL.createObjectURL(new Blob([response.data], { type: 'application/zip' }))
    const a = document.createElement('a')
    a.href = url
    a.download = filename || `output_${id}.zip`
    a.click()
    URL.revokeObjectURL(url)
}
