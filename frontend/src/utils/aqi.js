export const getAQIColor = (aqi) => {
  if (aqi === null || aqi === undefined) return '#718096'
  if (aqi <= 50) return '#00E400'  // Green - Good
  if (aqi <= 100) return '#FFFF00' // Yellow - Moderate
  if (aqi <= 150) return '#FF7E00' // Orange - Unhealthy for Sensitive Groups
  if (aqi <= 200) return '#FF0000' // Red - Unhealthy
  if (aqi <= 300) return '#8F3F97' // Purple - Very Unhealthy
  return '#7E0023'                 // Maroon - Hazardous
}

export const getAQICategory = (aqi) => {
  if (aqi === null || aqi === undefined) return 'Unknown'
  if (aqi <= 50) return 'Good'
  if (aqi <= 100) return 'Moderate'
  if (aqi <= 150) return 'Unhealthy for Sensitive Groups'
  if (aqi <= 200) return 'Unhealthy'
  if (aqi <= 300) return 'Very Unhealthy'
  return 'Hazardous'
}

export const getAQIDescription = (aqi) => {
  if (aqi === null || aqi === undefined) return 'No data available'
  if (aqi <= 50) return 'Air quality is satisfactory, and air pollution poses little or no risk.'
  if (aqi <= 100) return 'Air quality is acceptable. However, there may be a risk for some people, particularly those who are unusually sensitive to air pollution.'
  if (aqi <= 150) return 'Members of sensitive groups may experience health effects. The general public is less likely to be affected.'
  if (aqi <= 200) return 'Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects.'
  if (aqi <= 300) return 'Health alert: The risk of health effects is increased for everyone.'
  return 'Health warning of emergency conditions: everyone is more likely to be affected.'
}

export const aqiLegend = [
  { min: 0, max: 50, color: '#00E400', label: 'Good' },
  { min: 51, max: 100, color: '#FFFF00', label: 'Moderate' },
  { min: 101, max: 150, color: '#FF7E00', label: 'Unhealthy for Sensitive' },
  { min: 151, max: 200, color: '#FF0000', label: 'Unhealthy' },
  { min: 201, max: 300, color: '#8F3F97', label: 'Very Unhealthy' },
  { min: 301, max: 500, color: '#7E0023', label: 'Hazardous' },
]

