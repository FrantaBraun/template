export type AttributeType = 'text' | 'number' | 'boolean' | 'date'
export type AttributeBucket = 'user_data' | 'system_data'

export interface UserAttribute {
  key: string
  bucket: AttributeBucket
  type: AttributeType
  required: boolean
  i18nKey: string
}

interface ConfigFile {
  attributes?: UserAttribute[]
}

/**
 * Loads the user_data attributes declared in public/config.json. system_data
 * entries are dropped here (with a dev warning) rather than deeper in the
 * form - this app's credentials can never read or write system_data on the
 * auth service (confirmed against its own OpenAPI schema), so rendering one
 * would just produce a field that silently fails to save.
 */
export async function loadUserAttributes(): Promise<UserAttribute[]> {
  const resp = await fetch('/config.json')
  if (!resp.ok) return []
  const config: ConfigFile = await resp.json()
  const attributes = config.attributes ?? []

  return attributes.filter((attribute) => {
    if (attribute.bucket === 'system_data') {
      console.warn(
        `config.json: attribute "${attribute.key}" is tagged system_data and will not be rendered - ` +
          'this app has no credentials to read or write system_data on the auth service.',
      )
      return false
    }
    return true
  })
}
