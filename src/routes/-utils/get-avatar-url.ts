import { Avatar } from '../_auth/register/-constants'

export function getAvatarUrl(avatar: Avatar) {
  return `/images/${avatar}.png`
}
