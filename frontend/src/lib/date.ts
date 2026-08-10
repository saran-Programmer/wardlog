export function dateAtMinutes(base: Date, minutesFromMidnight: number): Date {
  const date = new Date(base.getFullYear(), base.getMonth(), base.getDate())
  date.setMinutes(minutesFromMidnight)
  return date
}

export function toDateInputValue(date: Date): string {
  const pad = (value: number) => value.toString().padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
}

export function toTimeInputValue(date: Date): string {
  const pad = (value: number) => value.toString().padStart(2, '0')
  return `${pad(date.getHours())}:${pad(date.getMinutes())}`
}

export function combineDateAndTime(dateValue: string, timeValue: string): Date {
  const [year, month, day] = dateValue.split('-').map(Number)
  const [hours, minutes] = timeValue.split(':').map(Number)
  return new Date(year, month - 1, day, hours, minutes)
}

export function formatDuration(minutes: number): string {
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  if (hours === 0) return `${mins}m`
  if (mins === 0) return `${hours}h`
  return `${hours}h ${mins}m`
}

export function toLocalDateTimeString(date: Date): string {
  const pad = (value: number) => value.toString().padStart(2, '0')
  const datePart = `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
  const timePart = `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
  return `${datePart}T${timePart}`
}
