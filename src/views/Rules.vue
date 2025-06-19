<template>
  <page-container>
    <div class="rules">
      <div class="page-header">
        <h2 class="page-title">规则配置</h2>
      </div>

      <!-- 规则配置部分 -->
      <el-card class="box-card">
        <template #header>
          <div class="card-header">
            <span>规则配置</span>
            <el-button type="primary" @click="handleSaveRules">
              <el-icon><Check /></el-icon>
              保存规则
            </el-button>
          </div>
        </template>
        <div id="rulesEditor" style="width: 100%; height: 400px;"></div>
      </el-card>

      <!-- 规则集配置部分 -->
      <el-card class="box-card">
        <template #header>
          <div class="card-header">
            <span>规则集配置</span>
            <el-button type="primary" @click="handleSaveRuleSets">
              <el-icon><Check /></el-icon>
              保存规则集
            </el-button>
          </div>
        </template>
        <div id="ruleSetsEditor" style="width: 100%; height: 400px;"></div>
      </el-card>

      <!-- 规则对话框 -->
      <el-dialog
        v-model="ruleDialog.visible"
        :title="ruleDialog.isEdit ? '编辑规则' : '添加规则'"
        width="600px"
        class="modern-dialog"
      >
        <div class="modern-dialog-body">
          <el-form :model="ruleDialog.form" :rules="ruleDialog.rules" ref="ruleFormRef" label-position="top" class="modern-form">
            <div class="form-section">
              <el-form-item label="action" prop="rules.action.action" required>
                <el-select v-model="ruleDialog.form.rules.action.action" placeholder="请选择action">
                  <el-option label="route" value="route" />
                  <el-option label="reject" value="reject" />
                  <el-option label="hijack-dns" value="hijack-dns" />
                  <el-option label="sniff" value="sniff" />
                </el-select>
              </el-form-item>
              <!-- 动态渲染route和reject相关表单项 -->
              <template v-if="ruleDialog.form.rules.action.action === 'route'">
                <el-form-item label="outbound" prop="rules.action.outbound" required>
                  <el-select v-model="ruleDialog.form.rules.action.outbound" placeholder="请选择outbound">
                    <el-option v-for="item in outboundOptions" :key="item" :label="item" :value="item" />
                  </el-select>
                </el-form-item>
              </template>
              <template v-if="ruleDialog.form.rules.action.action === 'reject'">
                <el-form-item label="method" prop="rules.action.method" required>
                  <el-select v-model="ruleDialog.form.rules.action.method" placeholder="请选择method">
                    <el-option label="default" value="default" />
                    <el-option label="drop" value="drop" />
                  </el-select>
                </el-form-item>
                <el-form-item label="no_drop">
                  <el-switch v-model="ruleDialog.form.rules.action.no_drop" active-value="true" inactive-value="false" />
                </el-form-item>
              </template>
              <template v-if="ruleDialog.form.rules.action.action === 'sniff'">
                <el-form-item label="sniffer">
                  <el-select v-model="ruleDialog.form.rules.action.sniffer" multiple placeholder="请选择sniffer">
                    <el-option label="http" value="http" />
                    <el-option label="tls" value="tls" />
                    <el-option label="quic" value="quic" />
                    <el-option label="stun" value="stun" />
                    <el-option label="dns" value="dns" />
                    <el-option label="bittorrent" value="bittorrent" />
                    <el-option label="dtls" value="dtls" />
                    <el-option label="ssh" value="ssh" />
                    <el-option label="rdp" value="rdp" />
                    <el-option label="ntp" value="ntp" />
                  </el-select>
                </el-form-item>
                <el-form-item label="timeout">
                  <el-input v-model="ruleDialog.form.rules.action.timeout" placeholder="请输入timeout" />
                </el-form-item>
              </template>
            </div>
            <div class="form-section">
              <el-form-item label="规则类型" required>
                <div class="rule-types" style="display: flex; align-items: center; gap: 8px;">
                  <el-select
                    v-model="ruleDialog.form.selectedTypes"
                    multiple
                    placeholder="请选择规则类型"
                    style="width: 320px"
                    value-key="value"
                    :collapse-tags="false"
                  >
                    <el-option
                      v-for="type in ruleTypes"
                      :key="type.value"
                      :label="type.label"
                      :value="type"
                    />
                  </el-select>
                  <el-button type="default" size="small" @click="ruleDialog.form.selectedTypes = []">清除</el-button>
                </div>
              </el-form-item>
            </div>
            <div class="form-section form-section-fields">
              <template v-for="type in ruleDialog.form.selectedTypes" :key="type.value">
                <!-- Domain 规则 -->
                <template v-if="type.value === 'domain'">
                  <el-form-item :label="type.value">
                    <el-input
                      v-model="ruleDialog.form.rules[type.value].domains"
                      type="textarea"
                      :rows="3"
                      placeholder="每行一个域名"
                    />
                  </el-form-item>
                </template>

                <!-- Domain Suffix 规则 -->
                <template v-if="type.value === 'domain_suffix'">
                  <el-form-item :label="type.value">
                    <el-input
                      v-model="ruleDialog.form.rules[type.value].domain_suffixes"
                      type="textarea"
                      :rows="3"
                      placeholder="每行一个域名后缀"
                    />
                  </el-form-item>
                </template>

                <!-- Domain Keyword 规则 -->
                <template v-if="type.value === 'domain_keyword'">
                  <el-form-item :label="type.value">
                    <el-input
                      v-model="ruleDialog.form.rules[type.value].keywords"
                      type="textarea"
                      :rows="3"
                      placeholder="每行一个关键词"
                    />
                  </el-form-item>
                </template>

                <!-- IP CIDR 规则 -->
                <template v-if="type.value === 'ip_cidr'">
                  <el-form-item :label="type.value">
                    <el-input
                      v-model="ruleDialog.form.rules[type.value].ip_cidr"
                      type="textarea"
                      :rows="3"
                      placeholder="每行一个IP CIDR"
                    />
                  </el-form-item>
                </template>

                <!-- 端口规则 -->
                <template v-if="type.value === 'port'">
                  <el-form-item :label="type.value">
                    <el-input
                      v-model="ruleDialog.form.rules[type.value].ports"
                      type="textarea"
                      :rows="3"
                      placeholder="每行一个端口"
                    />
                  </el-form-item>
                </template>

                <!-- 端口范围规则 -->
                <template v-if="type.value === 'port_range'">
                  <el-form-item :label="type.value">
                    <el-input
                      v-model="ruleDialog.form.rules[type.value].port_ranges"
                      type="textarea"
                      :rows="3"
                      placeholder="每行一个端口范围，格式：起始端口-结束端口"
                    />
                  </el-form-item>
                </template>

                <!-- 源端口规则 -->
                <template v-if="type.value === 'source_port'">
                  <el-form-item :label="type.value">
                    <el-input
                      v-model="ruleDialog.form.rules[type.value].ports"
                      type="textarea"
                      :rows="3"
                      placeholder="每行一个源端口"
                    />
                  </el-form-item>
                </template>

                <!-- 源端口范围规则 -->
                <template v-if="type.value === 'source_port_range'">
                  <el-form-item :label="type.value">
                    <el-input
                      v-model="ruleDialog.form.rules[type.value].port_ranges"
                      type="textarea"
                      :rows="3"
                      placeholder="每行一个源端口范围，格式：起始端口-结束端口"
                    />
                  </el-form-item>
                </template>

                <!-- 进程名规则 -->
                <template v-if="type.value === 'process_name'">
                  <el-form-item :label="type.value">
                    <el-input
                      v-model="ruleDialog.form.rules[type.value].process_names"
                      type="textarea"
                      :rows="3"
                      placeholder="每行一个进程名"
                    />
                  </el-form-item>
                </template>

                <!-- 进程路径规则 -->
                <template v-if="type.value === 'process_path'">
                  <el-form-item :label="type.value">
                    <el-input
                      v-model="ruleDialog.form.rules[type.value].process_paths"
                      type="textarea"
                      :rows="3"
                      placeholder="每行一个进程路径"
                    />
                  </el-form-item>
                </template>

                <!-- 包名规则 -->
                <template v-if="type.value === 'package_name'">
                  <el-form-item :label="type.value">
                    <el-input
                      v-model="ruleDialog.form.rules[type.value].package_names"
                      type="textarea"
                      :rows="3"
                      placeholder="每行一个包名"
                    />
                  </el-form-item>
                </template>

                <!-- 用户规则 -->
                <template v-if="type.value === 'user'">
                  <el-form-item :label="type.value">
                    <el-input
                      v-model="ruleDialog.form.rules[type.value].users"
                      type="textarea"
                      :rows="3"
                      placeholder="每行一个用户名"
                    />
                  </el-form-item>
                </template>

                <!-- 用户ID规则 -->
                <template v-if="type.value === 'user_id'">
                  <el-form-item :label="type.value">
                    <el-input
                      v-model="ruleDialog.form.rules[type.value].user_ids"
                      type="textarea"
                      :rows="3"
                      placeholder="每行一个用户ID"
                    />
                  </el-form-item>
                </template>

                <!-- WIFISSID规则 -->
                <template v-if="type.value === 'wifi_ssid'">
                  <el-form-item :label="type.value">
                    <el-input
                      v-model="ruleDialog.form.rules[type.value].ssids"
                      type="textarea"
                      :rows="3"
                      placeholder="每行一个WIFI SSID"
                    />
                  </el-form-item>
                </template>

                <!-- WIFIBSSID规则 -->
                <template v-if="type.value === 'wifi_bssid'">
                  <el-form-item :label="type.value">
                    <el-input
                      v-model="ruleDialog.form.rules[type.value].bssids"
                      type="textarea"
                      :rows="3"
                      placeholder="每行一个WIFI BSSID"
                    />
                  </el-form-item>
                </template>

                <!-- IP版本规则 -->
                <template v-if="type.value === 'ip_version'">
                  <el-form-item :label="type.value">
                    <el-select v-model="ruleDialog.form.rules[type.value].version" placeholder="请选择IP版本">
                      <el-option label="IPv4" value="4" />
                      <el-option label="IPv6" value="6" />
                    </el-select>
                  </el-form-item>
                </template>

                <!-- protocol 规则 -->
                <template v-if="type.value === 'protocol'">
                  <el-form-item :label="type.value">
                    <el-select v-model="ruleDialog.form.rules[type.value].protocols" multiple placeholder="请选择protocol">
                      <el-option label="http" value="http" />
                      <el-option label="tls" value="tls" />
                      <el-option label="quic" value="quic" />
                      <el-option label="stun" value="stun" />
                      <el-option label="dns" value="dns" />
                      <el-option label="bittorrent" value="bittorrent" />
                      <el-option label="dtls" value="dtls" />
                      <el-option label="ssh" value="ssh" />
                      <el-option label="rdp" value="rdp" />
                      <el-option label="ntp" value="ntp" />
                    </el-select>
                  </el-form-item>
                </template>

                <!-- inbound 多行输入框 -->
                <template v-if="type.value === 'inbound'">
                  <el-form-item :label="type.value">
                    <el-input v-model="ruleDialog.form.rules[type.value].inbound" type="textarea" :rows="3" placeholder="每行一个inbound" />
                  </el-form-item>
                </template>
                <!-- auth_user 多行输入框 -->
                <template v-if="type.value === 'auth_user'">
                  <el-form-item :label="type.value">
                    <el-input v-model="ruleDialog.form.rules[type.value].auth_user" type="textarea" :rows="3" placeholder="每行一个auth_user" />
                  </el-form-item>
                </template>
                <!-- domain_regex 多行输入框 -->
                <template v-if="type.value === 'domain_regex'">
                  <el-form-item :label="type.value">
                    <el-input v-model="ruleDialog.form.rules[type.value].domain_regex" type="textarea" :rows="3" placeholder="每行一个domain_regex" />
                  </el-form-item>
                </template>
                <!-- source_ip_cidr 多行输入框 -->
                <template v-if="type.value === 'source_ip_cidr'">
                  <el-form-item :label="type.value">
                    <el-input v-model="ruleDialog.form.rules[type.value].source_ip_cidr" type="textarea" :rows="3" placeholder="每行一个source_ip_cidr" />
                  </el-form-item>
                </template>
                <!-- process_path_regex 多行输入框 -->
                <template v-if="type.value === 'process_path_regex'">
                  <el-form-item :label="type.value">
                    <el-input v-model="ruleDialog.form.rules[type.value].process_path_regex" type="textarea" :rows="3" placeholder="每行一个process_path_regex" />
                  </el-form-item>
                </template>

                <!-- client 规则 -->
                <template v-if="type.value === 'client'">
                  <el-form-item :label="type.value">
                    <el-select v-model="ruleDialog.form.rules[type.value].client" placeholder="请选择client">
                      <el-option label="chromium" value="chromium" />
                      <el-option label="safari" value="safari" />
                      <el-option label="firefox" value="firefox" />
                      <el-option label="quic-go" value="quic-go" />
                    </el-select>
                  </el-form-item>
                </template>

                <!-- rule_set_ip_cidr_match_source 规则 -->
                <template v-if="type.value === 'rule_set_ip_cidr_match_source'">
                  <el-form-item :label="type.value">
                    <el-switch v-model="ruleDialog.form.rules[type.value].rule_set_ip_cidr_match_source" active-value="true" inactive-value="false" />
                  </el-form-item>
                </template>
                
                <!-- 其余类型保持不变 -->
                <template v-if="type.value === 'network'">
                  <el-form-item :label="type.value">
                    <el-select v-model="ruleDialog.form.rules[type.value].network" placeholder="请选择network">
                      <el-option label="tcp" value="tcp" />
                      <el-option label="udp" value="udp" />
                    </el-select>
                  </el-form-item>
                </template>

                <!-- network_type 规则 -->
                <template v-if="type.value === 'network_type'">
                  <el-form-item :label="type.value">
                    <el-select v-model="ruleDialog.form.rules[type.value].network_type" placeholder="请选择network_type">
                      <el-option label="wifi" value="wifi" />
                      <el-option label="cellular" value="cellular" />
                      <el-option label="ethernet" value="ethernet" />
                      <el-option label="other" value="other" />
                    </el-select>
                  </el-form-item>
                </template>

                <!-- invert 规则 -->
                <template v-if="type.value === 'invert'">
                  <el-form-item :label="type.value">
                    <el-switch v-model="ruleDialog.form.rules[type.value].invert" active-value="true" inactive-value="false" />
                  </el-form-item>
                </template>

                <!-- source_ip_is_private 规则 -->
                <template v-if="type.value === 'source_ip_is_private'">
                  <el-form-item :label="type.value">
                    <el-switch v-model="ruleDialog.form.rules[type.value].source_ip_is_private" active-value="true" inactive-value="false" />
                  </el-form-item>
                </template>

                <!-- ip_is_private 规则 -->
                <template v-if="type.value === 'ip_is_private'">
                  <el-form-item :label="type.value">
                    <el-switch v-model="ruleDialog.form.rules[type.value].ip_is_private" active-value="true" inactive-value="false" />
                  </el-form-item>
                </template>

                <!-- clash_mode 规则 -->
                <template v-if="type.value === 'clash_mode'">
                  <el-form-item :label="type.value">
                    <el-input v-model="ruleDialog.form.rules[type.value].clash_mode" placeholder="请输入clash_mode" />
                  </el-form-item>
                </template>

                <!-- network_is_expensive 规则 -->
                <template v-if="type.value === 'network_is_expensive'">
                  <el-form-item :label="type.value">
                    <el-switch v-model="ruleDialog.form.rules[type.value].network_is_expensive" active-value="true" inactive-value="false" />
                  </el-form-item>
                </template>

                <!-- network_is_constrained 规则 -->
                <template v-if="type.value === 'network_is_constrained'">
                  <el-form-item :label="type.value">
                    <el-switch v-model="ruleDialog.form.rules[type.value].network_is_constrained" active-value="true" inactive-value="false" />
                  </el-form-item>
                </template>
              </template>
            </div>
          </el-form>
        </div>
        <template #footer>
          <div class="dialog-footer-modern">
            <el-button @click="ruleDialog.visible = false">取消</el-button>
            <el-button type="primary" @click="handleSaveRule">确定</el-button>
          </div>
        </template>
      </el-dialog>

      <!-- 规则集对话框 -->
      <el-dialog
        v-model="ruleSetDialog.visible"
        title="添加规则集"
        width="600px"
        class="modern-dialog"
      >
        <div class="modern-dialog-body">
          <el-form :model="ruleSetDialog.form" label-position="top" class="modern-form">
            <el-form-item label="type" required>
              <el-select v-model="ruleSetDialog.form.type" placeholder="请选择类型">
                <el-option label="inline" value="inline" />
                <el-option label="local" value="local" />
                <el-option label="remote" value="remote" />
              </el-select>
            </el-form-item>
            <el-form-item label="tag" required>
              <el-input v-model="ruleSetDialog.form.tag" placeholder="请输入tag" />
            </el-form-item>
            <template v-if="ruleSetDialog.form.type === 'inline'">
              <div class="form-section form-section-fields">
                <template v-for="(rule, idx) in ruleSetDialog.form.rules" :key="idx">
                  <el-card class="mb-2">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                      <span>规则{{ idx + 1 }}</span>
                      <el-button type="danger" size="small" @click="removeInlineRule(idx)">删除</el-button>
                    </div>
                    <el-form-item label="type" required>
                      <el-select v-model="rule.type" placeholder="请选择规则类型">
                        <el-option v-for="type in inlineRuleTypes" :key="type.value" :label="type.label" :value="type.value" />
                      </el-select>
                    </el-form-item>
                    <template v-if="rule.type">
                      <el-form-item :label="rule.type" required>
                        <template v-if="inlineRuleTypes.find(t => t.value === rule.type).input === 'textarea'">
                          <el-input v-model="rule.value" type="textarea" :rows="3" :placeholder="'请输入' + rule.type + '，每行一项'" />
                        </template>
                        <template v-else-if="inlineRuleTypes.find(t => t.value === rule.type).input === 'select'">
                          <el-select v-model="rule.value" :placeholder="'请选择' + rule.type">
                            <el-option v-for="opt in inlineRuleTypes.find(t => t.value === rule.type).options" :key="opt" :label="opt" :value="opt" />
                          </el-select>
                        </template>
                        <template v-else-if="inlineRuleTypes.find(t => t.value === rule.type).input === 'switch'">
                          <el-switch v-model="rule.value" active-value="true" inactive-value="false" />
                        </template>
                      </el-form-item>
                    </template>
                  </el-card>
                </template>
                <el-button type="primary" plain icon="el-icon-plus" @click="addInlineRule">添加规则</el-button>
              </div>
            </template>
            <template v-if="ruleSetDialog.form.type === 'local'">
              <el-form-item label="format" required>
                <el-select v-model="ruleSetDialog.form.format" placeholder="请选择format">
                  <el-option label="source" value="source" />
                  <el-option label="binary" value="binary" />
                </el-select>
              </el-form-item>
              <el-form-item label="path" required>
                <el-input v-model="ruleSetDialog.form.path" placeholder="请输入path" />
              </el-form-item>
            </template>
            <template v-if="ruleSetDialog.form.type === 'remote'">
              <el-form-item label="format" required>
                <el-select v-model="ruleSetDialog.form.format" placeholder="请选择format">
                  <el-option label="source" value="source" />
                  <el-option label="binary" value="binary" />
                </el-select>
              </el-form-item>
              <el-form-item label="url" required>
                <el-input v-model="ruleSetDialog.form.url" placeholder="请输入url" />
              </el-form-item>
              <el-form-item label="download_detour">
                <el-select v-model="ruleSetDialog.form.download_detour" placeholder="请选择download_detour">
                  <el-option v-for="item in outboundOptions" :key="item" :label="item" :value="item" />
                </el-select>
              </el-form-item>
              <el-form-item label="update_interval">
                <el-input v-model="ruleSetDialog.form.update_interval" placeholder="请输入update_interval" />
              </el-form-item>
            </template>
          </el-form>
        </div>
        <template #footer>
          <div class="dialog-footer-modern">
            <el-button @click="ruleSetDialog.visible = false">取消</el-button>
            <el-button type="primary" @click="handleSaveRuleSet">确定</el-button>
          </div>
        </template>
      </el-dialog>
    </div>
  </page-container>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import { Plus, Edit, Delete, Check } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageContainer from '../components/PageContainer.vue'
import { globalConfig } from '../globalConfig'
import JSONEditor from 'jsoneditor'
import 'jsoneditor/dist/jsoneditor.css'

// 规则类型选项（移除action）
const ruleTypes = [
  { label: 'domain', value: 'domain' },
  { label: 'domain_suffix', value: 'domain_suffix' },
  { label: 'domain_keyword', value: 'domain_keyword' },
  { label: 'ip_cidr', value: 'ip_cidr' },
  { label: 'port', value: 'port' },
  { label: 'port_range', value: 'port_range' },
  { label: 'source_port', value: 'source_port' },
  { label: 'source_port_range', value: 'source_port_range' },
  { label: 'process_name', value: 'process_name' },
  { label: 'process_path', value: 'process_path' },
  { label: 'package_name', value: 'package_name' },
  { label: 'user', value: 'user' },
  { label: 'user_id', value: 'user_id' },
  { label: 'wifi_ssid', value: 'wifi_ssid' },
  { label: 'wifi_bssid', value: 'wifi_bssid' },
  { label: 'ip_version', value: 'ip_version' },
  { label: 'protocol', value: 'protocol' },
  { label: 'inbound', value: 'inbound' },
  { label: 'auth_user', value: 'auth_user' },
  { label: 'client', value: 'client' },
  { label: 'network', value: 'network' },
  { label: 'domain_regex', value: 'domain_regex' },
  { label: 'source_ip_cidr', value: 'source_ip_cidr' },
  { label: 'source_ip_is_private', value: 'source_ip_is_private' },
  { label: 'ip_is_private', value: 'ip_is_private' },
  { label: 'process_path_regex', value: 'process_path_regex' },
  { label: 'clash_mode', value: 'clash_mode' },
  { label: 'network_type', value: 'network_type' },
  { label: 'network_is_expensive', value: 'network_is_expensive' },
  { label: 'network_is_constrained', value: 'network_is_constrained' },
  { label: 'rule_set', value: 'rule_set' },
  { label: 'rule_set_ip_cidr_match_source', value: 'rule_set_ip_cidr_match_source' },
  { label: 'invert', value: 'invert' }
]

// 国家/地区选项（示例）
const countries = [
  { label: '中国', value: 'CN' },
  { label: '美国', value: 'US' },
  { label: '日本', value: 'JP' },
  { label: '韩国', value: 'KR' }
]

// 规则相关
const rules = ref([])
const ruleDialog = reactive({
  visible: false,
  isEdit: false,
  form: {
    name: '',
    selectedTypes: [],
    rules: {}
  },
  rules: {}
})

// 规则集相关
const ruleSets = ref([])
const ruleSetDialog = reactive({
  visible: false,
  isEdit: false,
  form: {
    type: '',
    tag: '',
    format: '',
    path: '',
    url: '',
    download_detour: '',
    update_interval: '',
    rules: []
  }
})

// 在script setup中添加outboundOptions
const outboundOptions = ref([])

// 获取所有 outbounds
const fetchOutbounds = async () => {
  try {
    console.log('开始获取 outbounds...')
    const response = await fetch('/api/outbounds')
    const data = await response.json()
    console.log('获取到的 outbounds 数据:', data)
    if (data.success) {
      outboundOptions.value = data.outbounds
      console.log('更新后的 outboundOptions:', outboundOptions.value)
    } else {
      ElMessage.error('获取 outbounds 失败：' + data.error)
    }
  } catch (error) {
    console.error('获取 outbounds 出错:', error)
    ElMessage.error('获取 outbounds 失败：' + error.message)
  }
}

// 在script setup中添加inlineRuleTypes
const inlineRuleTypes = [
  { label: 'query_type', value: 'query_type', input: 'textarea' },
  { label: 'network', value: 'network', input: 'select', options: ['tcp', 'udp'] },
  { label: 'domain', value: 'domain', input: 'textarea' },
  { label: 'domain_suffix', value: 'domain_suffix', input: 'textarea' },
  { label: 'domain_keyword', value: 'domain_keyword', input: 'textarea' },
  { label: 'domain_regex', value: 'domain_regex', input: 'textarea' },
  { label: 'source_ip_cidr', value: 'source_ip_cidr', input: 'textarea' },
  { label: 'ip_cidr', value: 'ip_cidr', input: 'textarea' },
  { label: 'source_port', value: 'source_port', input: 'textarea' },
  { label: 'source_port_range', value: 'source_port_range', input: 'textarea' },
  { label: 'port', value: 'port', input: 'textarea' },
  { label: 'port_range', value: 'port_range', input: 'textarea' },
  { label: 'process_name', value: 'process_name', input: 'textarea' },
  { label: 'process_path', value: 'process_path', input: 'textarea' },
  { label: 'process_path_regex', value: 'process_path_regex', input: 'textarea' },
  { label: 'package_name', value: 'package_name', input: 'textarea' },
  { label: 'network_type', value: 'network_type', input: 'select', options: ['wifi', 'cellular', 'ethernet', 'other'] },
  { label: 'network_is_expensive', value: 'network_is_expensive', input: 'switch' },
  { label: 'network_is_constrained', value: 'network_is_constrained', input: 'switch' },
  { label: 'wifi_ssid', value: 'wifi_ssid', input: 'textarea' },
  { label: 'wifi_bssid', value: 'wifi_bssid', input: 'textarea' },
  { label: 'invert', value: 'invert', input: 'switch' }
]

// 获取规则类型标签
const getRuleTypeLabel = (type) => {
  const found = ruleTypes.find(t => t.value === type)
  return found ? found.label : type
}

// 在 script setup 中添加
const ruleFormRef = ref(null)

// 修改 handleSaveRule 函数
const handleSaveRule = async () => {
  if (!ruleFormRef.value) return
  
  try {
    await ruleFormRef.value.validate()
    
    if (!ruleDialog.form.name || !ruleDialog.form.selectedTypes.length) {
      ElMessage.warning('请填写完整信息')
      return
    }

    // 构建规则数据
    const ruleData = {
      name: ruleDialog.form.name,
      rules: {}
    }
    
    // 保存 action
    ruleData.rules.action = ruleDialog.form.rules.action
    
    // 只保存已选择的规则类型的数据
    ruleDialog.form.selectedTypes.forEach(type => {
      const ruleValue = ruleDialog.form.rules[type.value]
      // 只保存有值的字段
      const filteredRule = {}
      for (const [key, value] of Object.entries(ruleValue)) {
        if (value !== '' && value !== null && value !== undefined) {
          if (Array.isArray(value) && value.length > 0) {
            filteredRule[key] = value
          } else if (!Array.isArray(value)) {
            filteredRule[key] = value
          }
        }
      }
      if (Object.keys(filteredRule).length > 0) {
        ruleData.rules[type.value] = filteredRule
      }
    })

    console.log('保存的规则数据:', ruleData)

    if (ruleDialog.isEdit) {
      const index = rules.value.findIndex(item => item.name === ruleDialog.form.name)
      if (index > -1) {
        rules.value[index] = {
          ...ruleData,
          type: ruleDialog.form.selectedTypes.map(type => type.label).join(', '),
          content: JSON.stringify(ruleData.rules, null, 2)
        }
      }
    } else {
      if (rules.value.some(item => item.name === ruleDialog.form.name)) {
        ElMessage.warning('已存在同名规则')
        return
      }
      rules.value.push({
        ...ruleData,
        type: ruleDialog.form.selectedTypes.map(type => type.label).join(', '),
        content: JSON.stringify(ruleData.rules, null, 2)
      })
    }

    ruleDialog.visible = false
    ElMessage.success(ruleDialog.isEdit ? '编辑成功' : '添加成功')
  } catch (error) {
    console.error('表单验证失败:', error)
    ElMessage.error('请填写必填项')
  }
}

// 修改 initRuleForm 函数
const initRuleForm = () => {
  const form = {
    name: '',
    selectedTypes: [],
    rules: {}
  }
  
  // 为每种规则类型初始化对应的数据结构
  ruleTypes.forEach(type => {
    form.rules[type.value] = {
      domains: '',
      domain_suffixes: '',
      keywords: '',
      ip_cidr: '',
      ports: '',
      port_ranges: '',
      process_names: '',
      process_paths: '',
      package_names: '',
      users: '',
      user_ids: '',
      ssids: '',
      bssids: '',
      version: '',
      protocols: [],
      network: '',
      network_type: '',
      invert: false,
      source_ip_is_private: false,
      ip_is_private: false,
      clash_mode: '',
      network_is_expensive: false,
      network_is_constrained: false,
      action: {
        action: 'route',
        outbound: '',
        method: 'default',
        no_drop: false,
        sniffer: [],
        timeout: ''
      },
      inbound: '',
      auth_user: '',
      domain_regex: '',
      source_ip_cidr: '',
      process_path_regex: '',
      client: '',
      rule_set_ip_cidr_match_source: false
    }
  })
  
  // action单独初始化
  form.rules.action = {
    action: 'route',
    outbound: '',
    method: 'default',
    no_drop: false,
    sniffer: [],
    timeout: ''
  }
  
  // 初始化验证规则
  ruleDialog.rules = {
    'rules.action.action': [
      { required: true, message: '请选择 action', trigger: 'change' }
    ],
    'rules.action.outbound': [
      { required: true, message: '请选择 outbound', trigger: 'change' }
    ],
    'rules.action.method': [
      { required: true, message: '请选择 method', trigger: 'change' }
    ]
  }
  
  return form
}

// 规则相关方法
const handleAddRule = () => {
  ruleDialog.isEdit = false
  ruleDialog.form = initRuleForm()
  ruleDialog.visible = true
}

const handleEditRule = (row) => {
  console.log('编辑规则:', row)
  ruleDialog.isEdit = true
  
  // 初始化表单
  const form = initRuleForm()
  
  // 设置规则名称
  form.name = row.name
  
  // 设置已选择的规则类型
  const selectedTypes = []
  const rules = row.rules
  
  for (const [key, value] of Object.entries(rules)) {
    if (key !== 'action' && value) {
      const ruleType = ruleTypes.find(type => type.value === key)
      if (ruleType) {
        selectedTypes.push(ruleType)
      }
    }
  }
  form.selectedTypes = selectedTypes
  
  // 设置规则内容
  for (const type of selectedTypes) {
    const value = rules[type.value]
    if (value) {
      console.log(`设置${type.value}值:`, value)
      
      // 根据规则类型设置对应的值
      switch (type.value) {
        case 'domain':
          form.rules[type.value].domains = value.domains || value || ''
          break
        case 'domain_suffix':
          form.rules[type.value].domain_suffixes = value.domain_suffixes || value || ''
          break
        case 'domain_keyword':
          form.rules[type.value].keywords = value.keywords || value || ''
          break
        case 'ip_cidr':
          form.rules[type.value].ip_cidr = value.ip_cidr || value || ''
          break
        case 'port':
          form.rules[type.value].ports = value.ports || value || ''
          break
        case 'port_range':
          form.rules[type.value].port_ranges = value.port_ranges || value || ''
          break
        case 'source_port':
          form.rules[type.value].ports = value.ports || value || ''
          break
        case 'source_port_range':
          form.rules[type.value].port_ranges = value.port_ranges || value || ''
          break
        case 'process_name':
          form.rules[type.value].process_names = value.process_names || value || ''
          break
        case 'process_path':
          form.rules[type.value].process_paths = value.process_paths || value || ''
          break
        case 'package_name':
          form.rules[type.value].package_names = value.package_names || value || ''
          break
        case 'user':
          form.rules[type.value].users = value.users || value || ''
          break
        case 'user_id':
          form.rules[type.value].user_ids = value.user_ids || value || ''
          break
        case 'wifi_ssid':
          form.rules[type.value].ssids = value.ssids || value || ''
          break
        case 'wifi_bssid':
          form.rules[type.value].bssids = value.bssids || value || ''
          break
        case 'ip_version':
          form.rules[type.value].version = value.version || value || ''
          break
        case 'protocol':
          form.rules[type.value].protocols = value.protocols || (Array.isArray(value) ? value : [value]) || []
          break
        case 'inbound':
          form.rules[type.value].inbound = value.inbound || value || ''
          break
        case 'auth_user':
          form.rules[type.value].auth_user = value.auth_user || value || ''
          break
        case 'domain_regex':
          form.rules[type.value].domain_regex = value.domain_regex || value || ''
          break
        case 'source_ip_cidr':
          form.rules[type.value].source_ip_cidr = value.source_ip_cidr || value || ''
          break
        case 'process_path_regex':
          form.rules[type.value].process_path_regex = value.process_path_regex || value || ''
          break
        case 'client':
          form.rules[type.value].client = value.client || value || ''
          break
        case 'network':
          form.rules[type.value].network = value.network || value || ''
          break
        case 'network_type':
          form.rules[type.value].network_type = value.network_type || value || ''
          break
        case 'invert':
          form.rules[type.value].invert = value.invert || value || false
          break
        case 'source_ip_is_private':
          form.rules[type.value].source_ip_is_private = value.source_ip_is_private || value || false
          break
        case 'ip_is_private':
          form.rules[type.value].ip_is_private = value.ip_is_private || value || false
          break
        case 'clash_mode':
          form.rules[type.value].clash_mode = value.clash_mode || value || ''
          break
        case 'network_is_expensive':
          form.rules[type.value].network_is_expensive = value.network_is_expensive || value || false
          break
        case 'network_is_constrained':
          form.rules[type.value].network_is_constrained = value.network_is_constrained || value || false
          break
        case 'rule_set_ip_cidr_match_source':
          form.rules[type.value].rule_set_ip_cidr_match_source = value.rule_set_ip_cidr_match_source || value || false
          break
      }
    }
  }
  
  // 设置 action
  if (rules.action) {
    console.log('设置action值:', rules.action)
    // 处理不同格式的 action
    if (typeof rules.action === 'string') {
      // 如果 action 是字符串，直接设置为 action 值
      form.rules.action.action = rules.action
    } else if (typeof rules.action === 'object') {
      // 如果 action 是对象，设置对象的各个属性
      form.rules.action = {
        action: rules.action.action || 'route',
        outbound: rules.action.outbound || '',
        method: rules.action.method || 'default',
        no_drop: rules.action.no_drop || false,
        sniffer: rules.action.sniffer || [],
        timeout: rules.action.timeout || ''
      }
    }
  }
  
  console.log('编辑表单数据:', form)
  ruleDialog.form = form
  ruleDialog.visible = true
}

const handleDeleteRule = (row) => {
  ElMessageBox.confirm('确定要删除该规则吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const index = rules.value.findIndex(item => item.name === row.name)
    if (index > -1) {
      rules.value.splice(index, 1)
      ElMessage.success('删除成功')
    }
  }).catch(() => {
    // 取消删除操作
  })
}

// 规则集相关方法
const handleAddRuleSet = () => {
  ruleSetDialog.visible = true
}

const handleEditRuleSet = (row) => {
  ruleSetDialog.form = { ...row }
  ruleSetDialog.visible = true
}

const handleDeleteRuleSet = (row) => {
  ElMessageBox.confirm('确定要删除该规则集吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const index = ruleSets.value.findIndex(item => item.name === row.name)
    if (index > -1) {
      ruleSets.value.splice(index, 1)
      ElMessage.success('删除成功')
    }
  }).catch(() => {
    // 取消删除操作
  })
}

const handleSaveRuleSet = () => {
  // 校验必填项
  if (!ruleSetDialog.form.type || !ruleSetDialog.form.tag) {
    ElMessage.warning('请填写完整信息')
    return
  }
  if (ruleSetDialog.form.type === 'inline' && ruleSetDialog.form.rules.length === 0) {
    ElMessage.warning('请至少添加一条规则')
    return
  }
  if (ruleSetDialog.form.type === 'local' && (!ruleSetDialog.form.format || !ruleSetDialog.form.path)) {
    ElMessage.warning('请填写完整信息')
    return
  }
  if (ruleSetDialog.form.type === 'remote' && (!ruleSetDialog.form.format || !ruleSetDialog.form.url)) {
    ElMessage.warning('请填写完整信息')
    return
  }

  const ruleSetData = {
    ...ruleSetDialog.form
  }

  if (ruleSetDialog.isEdit) {
    const index = ruleSets.value.findIndex(item => item.tag === ruleSetDialog.form.tag)
    if (index > -1) {
      ruleSets.value[index] = ruleSetData
    }
  } else {
    if (ruleSets.value.some(item => item.tag === ruleSetDialog.form.tag)) {
      ElMessage.warning('已存在同名规则集')
      return
    }
    ruleSets.value.push(ruleSetData)
  }

  // 更新全局配置
  globalConfig.route.rule_set = ruleSets.value

  ruleSetDialog.visible = false
  ElMessage.success(ruleSetDialog.isEdit ? '编辑成功' : '添加成功')
}

const addInlineRule = () => {
  ruleSetDialog.form.rules.push({ type: '', value: '' })
}

const removeInlineRule = (idx) => {
  ruleSetDialog.form.rules.splice(idx, 1)
}

// 规则和规则集内容
const rulesContent = ref('')
const ruleSetsContent = ref('')

// 获取所有规则
const fetchRules = async () => {
  try {
    console.log('开始获取规则...')
    const response = await fetch('/api/rules')
    const data = await response.json()
    console.log('获取到的规则数据:', data)
    if (data.success) {
      // 如果 rules 不存在，使用空数组
      const rules = data.rules || []
      console.log('设置规则数据:', rules)
      if (rulesEditor.value) {
        rulesEditor.value.set(rules)
      }
    } else {
      ElMessage.error('获取规则失败：' + data.error)
    }
  } catch (error) {
    console.error('获取规则出错:', error)
    ElMessage.error('获取规则失败：' + error.message)
  }
}

// 获取所有规则集
const fetchRuleSets = async () => {
  try {
    console.log('开始获取规则集...')
    const response = await fetch('/api/rule-sets')
    const data = await response.json()
    console.log('获取到的规则集数据:', data)
    if (data.success) {
      // 如果 rule_sets 不存在，使用空数组
      const ruleSets = data.rule_sets || []
      console.log('设置规则集数据:', ruleSets)
      if (ruleSetsEditor.value) {
        ruleSetsEditor.value.set(ruleSets)
      }
    } else {
      ElMessage.error('获取规则集失败：' + data.error)
    }
  } catch (error) {
    console.error('获取规则集出错:', error)
    ElMessage.error('获取规则集失败：' + error.message)
  }
}

// 保存规则
const handleSaveRules = async () => {
  try {
    // 从编辑器获取内容并验证JSON格式
    const rules = rulesEditor.value.get()
    
    // 发送保存请求
    const response = await fetch('/api/rules', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ rules })
    })
    
    const data = await response.json()
    if (data.success) {
      ElMessage.success('保存规则成功')
    } else {
      ElMessage.error('保存规则失败：' + data.error)
    }
  } catch (error) {
    console.error('保存规则出错:', error)
    ElMessage.error('保存规则失败：' + error.message)
  }
}

// 保存规则集
const handleSaveRuleSets = async () => {
  try {
    // 从编辑器获取内容并验证JSON格式
    const rule_sets = ruleSetsEditor.value.get()
    
    // 发送保存请求
    const response = await fetch('/api/rule-sets', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ rule_sets })
    })
    
    const data = await response.json()
    if (data.success) {
      ElMessage.success('保存规则集成功')
    } else {
      ElMessage.error('保存规则集失败：' + data.error)
    }
  } catch (error) {
    console.error('保存规则集出错:', error)
    ElMessage.error('保存规则集失败：' + error.message)
  }
}

// 在组件挂载时初始化数据
const initData = async () => {
  console.log('开始初始化数据...')
  // 获取所有规则
  await fetchRules()
  // 获取所有规则集
  await fetchRuleSets()
  
  // 从全局配置加载规则集
  if (globalConfig.route && globalConfig.route.rule_set) {
    ruleSets.value = [...globalConfig.route.rule_set]
  }
  console.log('数据初始化完成')
}

// 在组件挂载时初始化数据
onMounted(() => {
  // 先初始化编辑器
  initRulesEditor()
  initRuleSetsEditor()
  
  // 延迟一下再获取数据，确保编辑器已经完全初始化
  setTimeout(() => {
    fetchRules()
    fetchRuleSets()
  }, 100)
})

const rulesEditor = ref(null)
const ruleSetsEditor = ref(null)

// 初始化规则编辑器
const initRulesEditor = () => {
  const container = document.getElementById('rulesEditor')
  const options = {
    mode: 'code',
    modes: ['code', 'tree', 'view', 'form', 'text'],
    onError: function (err) {
      ElMessage.error('JSON 格式错误：' + err.toString())
    },
    mainMenuBar: true,
    navigationBar: false,
    statusBar: true,
    colorPicker: false,
    search: true,
    format: true,
    repair: true
  }
  rulesEditor.value = new JSONEditor(container, options)
  
  // 获取规则配置
  fetchRules()
}

// 初始化规则集编辑器
const initRuleSetsEditor = () => {
  const container = document.getElementById('ruleSetsEditor')
  const options = {
    mode: 'code',
    modes: ['code', 'tree', 'view', 'form', 'text'],
    onError: function (err) {
      ElMessage.error('JSON 格式错误：' + err.toString())
    },
    mainMenuBar: true,
    navigationBar: false,
    statusBar: true,
    colorPicker: false,
    search: true,
    format: true,
    repair: true
  }
  ruleSetsEditor.value = new JSONEditor(container, options)
  
  // 获取规则集配置
  fetchRuleSets()
}

onBeforeUnmount(() => {
  if (rulesEditor.value) {
    rulesEditor.value.destroy()
  }
  if (ruleSetsEditor.value) {
    ruleSetsEditor.value.destroy()
  }
})
</script>

<style scoped>
.rules {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
  color: #303133;
}

.box-card {
  margin-bottom: 20px;
  transition: all 0.3s;
}

.box-card:hover {
  box-shadow: 0 2px 12px 0 rgba(0,0,0,.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-textarea {
  font-family: monospace;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.rule-types {
  margin-bottom: 20px;
}

.el-divider {
  margin: 20px 0;
}

.el-divider__text {
  font-size: 16px;
  font-weight: 500;
}

.modern-dialog >>> .el-dialog__header {
  font-weight: bold;
  font-size: 20px;
  letter-spacing: 1px;
  padding-bottom: 8px;
}
.modern-dialog-body {
  background: #fafbfc;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  padding: 24px 18px 12px 18px;
}
.modern-form {
  margin: 0;
}
.form-section {
  margin-bottom: 18px;
  background: #fff;
  border-radius: 8px;
  padding: 16px 12px 8px 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}
.form-section-fields {
  margin-bottom: 0;
  padding-bottom: 0;
  box-shadow: none;
  background: transparent;
}
.el-form-item {
  margin-bottom: 16px;
}
.el-input, .el-select, .el-textarea {
  border-radius: 6px;
  min-height: 36px;
}
.dialog-footer-modern {
  display: flex;
  justify-content: center;
  gap: 18px;
  padding: 12px 0 0 0;
}
.el-button {
  border-radius: 6px;
  min-width: 80px;
  font-size: 15px;
}
.mb-2 { margin-bottom: 12px; }

:deep(.jsoneditor) {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

:deep(.jsoneditor-menu) {
  background-color: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
}

@media (max-width: 768px) {
  .rules {
    padding: 10px;
  }

  .page-title {
    font-size: 20px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .modern-dialog {
    --el-dialog-width: 95% !important;
  }
}
</style> 