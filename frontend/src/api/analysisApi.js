import axios from './authApi'

export async function createAnalysis(formData){
  // formData should include the `image` file (key: 'image')
  // TODO: backend currently only persists `image`; if you want to accept extra fields
  // (hair_visible, natural_hair, makeup, natural_light, colored_clothes) ensure
  // the server serializer accepts them. If not, remove extras.
  const res = await axios.post('/api/coloranalysis/analyze/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return res.data
}

export async function getHistory(){
  const res = await axios.get('/api/coloranalysis/history/')
  return res.data
}

export async function deleteAnalysis(id){
  const res = await axios.delete(`/api/coloranalysis/${id}/delete/`)
  return res.data
}

// Backend does not expose a detail endpoint for a single analysis by id.
// Frontend can fetch history and find the item by id. Consider adding
// GET /api/coloranalysis/<id>/ on the backend for direct access.
