import { DemoData } from '@/services/api'

interface DemoFormProps {
  values: DemoData
  onChange: (values: DemoData) => void
  errors?: string[]
}

const STATUS_OPTIONS = [
  { value: 'STUDENT', label: '在校生 / 刚毕业' },
  { value: 'JOB_SEEKING', label: '求职中 / 转职中' },
  { value: 'EMPLOYED', label: '全职在职' },
  { value: 'FREELANCER', label: '自由职业 / 创业中' },
  { value: 'OTHER', label: '其他状态' },
]

const INTEREST_OPTIONS = [
  '产品设计',
  '用户研究',
  '数据分析',
  '创业管理',
  '教育咨询',
  '科技创新',
  '心理辅导',
  '写作表达',
]

export function DemoForm({ values, onChange, errors }: DemoFormProps) {
  const handleFieldChange = <K extends keyof DemoData>(key: K, value: DemoData[K]) => {
    onChange({ ...values, [key]: value })
  }

  const GENDER_OPTIONS = [
    { value: 'MALE', label: '男' },
    { value: 'FEMALE', label: '女' },
    { value: 'OTHER', label: '其他' },
  ]
<<<<<<< HEAD

=======
  
>>>>>>> b218fc476dc540b3f1ff99140de32a837678d817
  const toggleInterest = (interest: string) => {
    // 将字符串按逗号分隔转为数组
    const interestsArray = values.interests ? values.interests.split(',').map(s => s.trim()).filter(Boolean) : []
    
    if (interestsArray.includes(interest)) {
      // 移除该兴趣
      const newArray = interestsArray.filter((item) => item !== interest)
      onChange({ ...values, interests: newArray.join(', ') })
    } else {
      // 添加该兴趣
      const newArray = [...interestsArray, interest]
      onChange({ ...values, interests: newArray.join(', ') })
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-lg font-semibold text-white">基础信息</h3>
        <p className="mt-1 text-sm text-slate-200/80">帮助我们了解你的背景，建立初始档案。</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-200">姓名</label>
          <input
            type="text"
            value={values.name}
            onChange={(e) => handleFieldChange('name', e.target.value)}
            placeholder="请填写你的姓名或常用称呼"
            className="w-full rounded-lg border border-white/20 bg-white/10 px-4 py-3 text-white placeholder:text-slate-300 focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-300/40"
          />
        </div>
<<<<<<< HEAD

              <div>
=======
      <div>
>>>>>>> b218fc476dc540b3f1ff99140de32a837678d817
          <label className="mb-2 block text-sm font-medium text-slate-200">性别</label>
          <select
            value={values.gender}
            onChange={(e) => handleFieldChange('gender', e.target.value)}
            className="w-full rounded-lg border border-white/20 bg-white/10 px-4 py-3 text-white focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-300/40"
          >
            <option value="" disabled>
              请选择
            </option>
            {GENDER_OPTIONS.map((option) => (
              <option key={option.value} value={option.value} className="text-gray-900">
                {option.label}
              </option>
            ))}
          </select>
<<<<<<< HEAD
        </div>

=======
        </div>       
>>>>>>> b218fc476dc540b3f1ff99140de32a837678d817
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-200">年龄</label>
          <input
            type="number"
            min={18}
            max={100}
            value={values.age || ''}
            onChange={(e) => handleFieldChange('age', Number(e.target.value))}
            placeholder="18 - 100"
            className="w-full rounded-lg border border-white/20 bg-white/10 px-4 py-3 text-white placeholder:text-slate-300 focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-300/40"
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-slate-200">当前状态</label>
          <select
            value={values.status}
            onChange={(e) => handleFieldChange('status', e.target.value)}
            className="w-full rounded-lg border border-white/20 bg-white/10 px-4 py-3 text-white focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-300/40"
          >
            <option value="" disabled>
              请选择
            </option>
            {STATUS_OPTIONS.map((option) => (
              <option key={option.value} value={option.value} className="text-gray-900">
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-slate-200">专业 / 领域</label>
          <input
            type="text"
            value={values.field}
            onChange={(e) => handleFieldChange('field', e.target.value)}
            placeholder="例如：UX 设计 / 数据科学 / 教育咨询"
            className="w-full rounded-lg border border-white/20 bg-white/10 px-4 py-3 text-white placeholder:text-slate-300 focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-300/40"
          />
        </div>
      </div>

      <div>
        <label className="mb-3 block text-sm font-medium text-slate-200">兴趣方向（可多选）</label>
        <div className="grid gap-3 sm:grid-cols-2">
          {INTEREST_OPTIONS.map((interest) => {
            // 将字符串按逗号分隔转为数组来检查
            const interestsArray = values.interests ? values.interests.split(',').map(s => s.trim()).filter(Boolean) : []
            const checked = interestsArray.includes(interest)
            return (
              <label
                key={interest}
                className={`flex cursor-pointer items-center gap-3 rounded-xl border px-4 py-3 transition-colors ${
                  checked
                    ? 'border-blue-400/60 bg-blue-500/10 text-white'
                    : 'border-white/10 bg-white/5 text-slate-200 hover:border-blue-300/40 hover:bg-blue-400/10'
                }`}
              >
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={() => toggleInterest(interest)}
                  className="h-4 w-4 rounded border-gray-300 text-blue-500 focus:ring-blue-400"
                />
                <span>{interest}</span>
              </label>
            )
          })}
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-200">当前所在城市</label>
          <input
            type="text"
            value={values.location}
            onChange={(e) => handleFieldChange('location', e.target.value)}
            placeholder="例如：上海 / 深圳 / 远程"
            className="w-full rounded-lg border border-white/20 bg-white/10 px-4 py-3 text-white placeholder:text-slate-300 focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-300/40"
          />
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-slate-200">期望未来所在地</label>
          <input
            type="text"
            value={values.future_location}
            onChange={(e) => handleFieldChange('future_location', e.target.value)}
            placeholder="例如：上海 / 北京 / 远程"
            className="w-full rounded-lg border border-white/20 bg-white/10 px-4 py-3 text-white placeholder:text-slate-300 focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-300/40"
          />
        </div>
      </div>

      {errors && errors.length > 0 && (
        <div className="rounded-xl border border-red-300/60 bg-red-500/10 p-4 text-sm text-red-200">
          <h4 className="font-semibold text-red-100">请完善以下信息：</h4>
          <ul className="mt-2 space-y-1">
            {errors.map((error, index) => (
              <li key={index}>• {error}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

