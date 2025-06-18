import { reactive } from 'vue'

export const globalConfig = reactive({
  log: {},
  dns: {},
  ntp: {},
  certificate: {},
  endpoints: [],
  inbounds: [],
  outbounds: [],
  route: {},
  services: [],
  experimental: {}
}) 