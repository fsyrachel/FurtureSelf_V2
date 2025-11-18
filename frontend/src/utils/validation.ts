export const validateDemoData = (data: any): string[] => {
  const errors: string[] = []

  if (!data.name || data.name.length < 1) {
    errors.push('请输入姓名')
  }
  if (!data.age || data.age < 18 || data.age > 100) {
    errors.push('年龄必须在18-100之间')
  }
  if (!data.gender) {
    errors.push('请选择性别')
  }
  if (!data.status) {
    errors.push('请选择当前状态')
  }
  if (!data.field) {
    errors.push('请输入专业领域')
  }
<<<<<<< HEAD
  if (!data.interests) {
=======
  if (!data.interests || data.interests.length < 1) {
>>>>>>> b218fc476dc540b3f1ff99140de32a837678d817
    errors.push('请至少选择一个兴趣方向')
  }
  if (!data.location) {
    errors.push('请输入当前位置')
  }
  if (!data.future_location) {
    errors.push('请输入期望位置')
  }

  return errors
}

export const validateValsData = (data: any): string[] => {
  const errors: string[] = []
  const fields = [
    'self_direction',
    'stimulation',
    'hedonism',
    'achievement',
    'power',
    'security',
    'conformity',
    'tradition',
    'benevolence',
    'universalism',
  ]

  fields.forEach((field) => {
    const value = data[field]
    if (value === undefined || value < 1 || value > 5) {
      errors.push(`${field} 必须是1-5之间的数字`)
    }
  })

  return errors
}

export const validateBFIData = (data: any): string[] => {
  const errors: string[] = []
  const fields = ['extraversion', 'agreeableness', 'conscientiousness', 'neuroticism', 'openness']

  fields.forEach((field) => {
    const value = data[field]
    if (value === undefined || value < 1.0 || value > 5.0) {
      errors.push(`${field} 必须是1.0-5.0之间的数字`)
    }
  })

  return errors
}
