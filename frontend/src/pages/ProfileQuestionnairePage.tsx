import { useMemo, useState, useEffect } from 'react'
import StarFieldLayout from '@/components/layouts/StarFieldLayout'
import { DemoForm } from '@/components/questionnaire/DemoForm'
import { PVQForm } from '@/components/questionnaire/PVQForm'
import { BFIForm } from '@/components/questionnaire/BFIForm'
import Button from '@/components/common/Button'
import { useUserStore } from '@/stores/userStore'
import apiClient, { BFIData, CurrentProfileCreate, DemoData, ValsData } from '@/services/api'
import {
  validateBFIData,
  validateDemoData,
  validateValsData,
} from '@/utils/validation'
import { useNavigate } from 'react-router-dom'

const steps = [
  { label: '1', title: '基本信息', desc: '基础背景、教育与工作情况，建立初始画像。' },
  { label: '2', title: '价值观收集 (PVQ-10)', desc: '识别核心驱动力与价值排序，锁定内在坐标。' },
  { label: '3', title: '大五人格测试 (BFI-5)', desc: '快速了解人格维度，辅助匹配未来角色。' },
]

const createDefaultDemoData = (): DemoData => ({
  name: '',
  age: 0,
  gender: '',
  status: '',
  field: '',
<<<<<<< HEAD
  interests: '',
=======
  interests: '',  // 后端期望字符串
>>>>>>> b218fc476dc540b3f1ff99140de32a837678d817
  location: '',
  future_location: '',
})

const createDefaultValsData = (): ValsData => ({
  self_direction: 3,
  stimulation: 3,
  hedonism: 3,
  achievement: 3,
  power: 3,
  security: 3,
  conformity: 3,
  tradition: 3,
  benevolence: 3,
  universalism: 3,
})

const createDefaultBFIData = (): BFIData => ({
  extraversion: 3,
  agreeableness: 3,
  conscientiousness: 3,
  neuroticism: 3,
  openness: 3,
})

export default function ProfileQuestionnairePage() {
  const navigate = useNavigate()
  const { userId, status, setStatus } = useUserStore((state) => ({
    userId: state.userId,
    status: state.status,
    setStatus: state.setStatus,
  }))

  const [currentStep, setCurrentStep] = useState(0)
  const [demoData, setDemoData] = useState<DemoData>(createDefaultDemoData)
  const [valsData, setValsData] = useState<ValsData>(createDefaultValsData)
  const [bfiData, setBFIData] = useState<BFIData>(createDefaultBFIData)

  // --- 新增: 步骤切换时自动滚动到顶部 ---
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [currentStep])

  // --- 1. 表单组件配置 ---
  const [stepErrors, setStepErrors] = useState<string[]>([])
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const progress = useMemo(() => ((currentStep + 1) / steps.length) * 100, [currentStep])

  const validateStep = (stepIndex: number): string[] => {
    switch (stepIndex) {
      case 0:
        return validateDemoData(demoData)
      case 1:
        return validateValsData(valsData)
      case 2:
        return validateBFIData(bfiData)
      default:
        return []
    }
  }

  const handleNext = () => {
    const errors = validateStep(currentStep)
    if (errors.length > 0) {
      setStepErrors(errors)
      return
    }
    setStepErrors([])
    setCurrentStep((prev) => prev + 1)
  }

  const handlePrev = () => {
    setStepErrors([])
    setCurrentStep((prev) => Math.max(prev - 1, 0))
  }

  const handleSubmit = async () => {
    const errors = [
      ...validateDemoData(demoData),
      ...validateValsData(valsData),
      ...validateBFIData(bfiData),
    ]

    if (errors.length > 0) {
      setStepErrors(errors)
      return
    }

    if (!userId) {
      setSubmitError('未找到用户信息，请返回重试或重新初始化。')
      return
    }

    const payload: CurrentProfileCreate = {
      demo_data: demoData,
      vals_data: valsData,
      bfi_data: bfiData,
    }

    try {
      setIsSubmitting(true)
      setSubmitError(null)

      const response = await apiClient.createCurrentProfile(userId, payload)

      if (response.status === 'CURRENT_PROFILE_SAVED') {
        setStatus('ONBOARDING')
        navigate('/profile/future')
      }

    } catch (error) {
      console.error('Failed to submit profile questionnaire', error)
      setSubmitError('提交失败，请稍后重试。')
    } finally {
      setIsSubmitting(false)
    }
  }

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return <DemoForm values={demoData} onChange={setDemoData} errors={stepErrors} />
      case 1:
        return <PVQForm values={valsData} onChange={setValsData} />
      case 2:
        return <BFIForm values={bfiData} onChange={setBFIData} errors={stepErrors} />
      default:
        return null
    }
  }

  if (status !== 'ONBOARDING') {
    return (
      <StarFieldLayout className="px-6 py-20">
        <div className="mx-auto max-w-2xl rounded-3xl border border-white/10 bg-white/10 p-10 text-center shadow-[0_30px_120px_-50px_rgba(64,136,255,0.6)]">
          <h1 className="text-3xl font-bold text-white">问卷已完成</h1>
          <p className="mt-4 text-base text-slate-200">
            当前档案问卷仅在新用户入职阶段开放。如果需要更新资料，请联系辅导员或等待后续功能。
          </p>
        </div>
      </StarFieldLayout>
    )
  }

  return (
    <StarFieldLayout className="px-6 py-16 md:px-12 lg:px-20 xl:px-32">
      <div className="mx-auto flex w-full max-w-[1100px] flex-col">
        <header className="mb-10">
          <p className="text-xs uppercase tracking-[0.45rem] text-sky-200/80">连接信标</p>
          <h1 className="mt-3 text-4xl font-extrabold text-white md:text-5xl">信标 01: 校准当前坐标
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-relaxed text-slate-200">
            接入深层时空网络，通过多维度问卷校准你的当前坐标。这是未来时空回信、洞见报告与个人成长航线的基础数据。
          </p>
        </header>

        <section className="rounded-[32px] border border-white/10 bg-white/8 p-10 shadow-[0_40px_120px_-45px_rgba(64,136,255,0.6)] backdrop-blur-xl">
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div>
                <div className="rounded-2xl border border-white/15 bg-white/10 px-4 py-2 text-xs uppercase tracking-[0.4rem] text-sky-100/80">
                  坐标校准进度
                </div>
                <h2 className="mt-4 text-2xl font-semibold text-white">
                  {steps[currentStep].title}
                </h2>
                <p className="mt-2 text-sm text-slate-200/85">{steps[currentStep].desc}</p>
              </div>
              <span className="rounded-full bg-blue-500/20 px-4 py-2 text-sm font-medium text-blue-100">
                {currentStep + 1} / {steps.length}
              </span>
            </div>

            <div className="mt-6 h-2 overflow-hidden rounded-full bg-white/15">
              <div
                className="h-full rounded-full bg-gradient-to-r from-sky-400 via-indigo-400 to-purple-500 transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>

            <div className="mt-6 grid gap-4 md:grid-cols-3">
              {steps.map((step, index) => {
                const active = index === currentStep
                const completed = index < currentStep
                return (
                  <div
                    key={step.label}
                    className={`rounded-2xl border px-4 py-4 text-sm transition-all ${
                      active
                        ? 'border-sky-400/60 bg-sky-500/15 text-white'
                        : completed
                        ? 'border-emerald-400/60 bg-emerald-500/10 text-emerald-100'
                        : 'border-white/10 bg-white/5 text-slate-200/85'
                    }`}
                  >
                    <p className="text-xs uppercase tracking-[0.3rem] text-slate-200/70">
                      阶段 {step.label}
                    </p>
                    <p className="mt-2 font-medium">{step.title}</p>
                  </div>
                )
              })}
            </div>
          </div>

          <div className="rounded-3xl border border-white/12 bg-[#0d1329]/70 p-8 shadow-[0_30px_120px_-50px_rgba(94,197,255,0.35)]">
            {renderStepContent()}

            {stepErrors.length > 0 && currentStep === 1 && (
              <div className="mt-6 rounded-xl border border-red-300/60 bg-red-500/10 p-4 text-sm text-red-200">
                <h4 className="font-semibold text-red-100">请完成所有数值填写：</h4>
                <ul className="mt-2 space-y-1">
                  {stepErrors.map((error, index) => (
                    <li key={index}>• {error}</li>
                  ))}
                </ul>
              </div>
            )}

            {submitError && (
              <div className="mt-6 rounded-xl border border-red-400/60 bg-red-500/10 p-4 text-sm text-red-200">
                {submitError}
              </div>
            )}

            <div className="mt-8 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div className="text-xs text-slate-300">
                机密协议：所有数据将加密传输至你的专属时空档案，仅用于生成个人航线分析。
              </div>
              <div className="flex flex-col gap-3 md:flex-row">
                {currentStep > 0 && (
                  <Button variant="outline" onClick={handlePrev}>
                    返回上一阶段
                  </Button>
                )}
                {currentStep < steps.length - 1 ? (
                  <Button onClick={handleNext}>进入下一阶段</Button>
                ) : (
                  <Button onClick={handleSubmit} loading={isSubmitting}>
                    确认坐标并进入下一步
                  </Button>
                )}
              </div>
            </div>
          </div>
        </section>
      </div>
    </StarFieldLayout>
  )
}

