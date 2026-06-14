import { getProfile } from './authApi'

export async function fetchProfile(){
  return getProfile()
}
