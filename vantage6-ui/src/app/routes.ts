export const routePaths = {
  login: '/auth/login',
  passwordLost: '/auth/password/lost',
  passwordRecover: '/auth/password/recover',
  setupMFA: '/auth/mfa/setup',
  mfaCode: '/auth/mfa/code',
  mfaLost: '/auth/mfa/lost',
  mfaRecover: '/auth/mfa/recover',
  home: '/',
  passwordChange: '/password/change',
  adminHome: '/admin',
  organizations: '/admin/organizations',
  organizationCreate: '/admin/organizations/create',
  organizationEdit: '/admin/organizations/edit',
  organization: '/admin/organizations',
  collaborations: '/admin/collaborations',
  collaborationCreate: '/admin/collaborations/create',
  collaborationEdit: '/admin/collaborations/edit',
  collaboration: '/admin/collaborations',
  algorithmStoreAdd: '/admin/collaborations/algorithm-stores/add',
  study: '/admin/collaborations/study',
  studyCreate: '/admin/collaborations/study/create',
  studyEdit: '/admin/collaborations/study/edit',
  roles: '/admin/roles',
  roleCreate: '/admin/roles/create',
  role: '/admin/roles',
  users: '/admin/users',
  userCreate: '/admin/users/create',
  userEdit: '/admin/users/edit',
  user: '/admin/users',
  nodes: '/admin/nodes',
  storeHome: '/store',
  stores: '/store/choose',
  store: '/store/store',
  algorithmsManage: '/store/algorithms',
  algorithmCreate: '/store/algorithms/create',
  algorithmEdit: '/store/algorithms/edit',
  algorithmManage: '/store/algorithms',
  analyzeHome: '/analyze',
  chooseCollaboration: '/analyze/collaboration/choose',
  keyUpload: '/analyze/key/upload',
  tasks: '/analyze/tasks',
  taskCreate: '/analyze/tasks/create',
  taskCreateRepeat: '/analyze/tasks/create/repeat',
  task: '/analyze/tasks',
  algorithms: '/analyze/algorithms',
  algorithm: '/analyze/algorithms',
  templateTaskCreate: '/analyze/template-tasks/create',
  storeUsers: '/store/users',
  storeUser: '/store/users',
  storeUserCreate: '/store/users/create',
  storeUserEdit: '/store/users/edit',
  storeRoles: '/store/roles',
  storeRole: '/store/roles',
  storeRoleCreate: '/store/roles/create',
  storeRoleEdit: '/store/roles/edit'
};

export const routerConfig = {
  login: 'login',
  passwordLost: 'password/lost',
  passwordRecover: 'password/recover',
  setupMFA: 'mfa/setup',
  mfaCode: 'mfa/code',
  mfaLost: 'mfa/lost',
  mfaRecover: 'mfa/recover',
  chooseCollaboration: 'collaboration/choose',
  keyUpload: 'key/upload',
  home: '',
  passwordChange: 'password/change',
  admin: 'admin',
  adminHome: '',
  organizations: 'organizations',
  organizationCreate: 'organizations/create',
  organizationEdit: 'organizations/edit/:id',
  organization: 'organizations/:id',
  collaborations: 'collaborations',
  collaborationCreate: 'collaborations/create',
  collaborationEdit: 'collaborations/edit/:id',
  collaboration: 'collaborations/:id',
  algorithmStoreAdd: 'collaborations/algorithm-stores/add/:id',
  study: 'collaborations/study/:id',
  studyEdit: 'collaborations/study/edit/:id',
  studyCreate: 'collaborations/study/create/:id',
  roles: 'roles',
  role: 'roles/:id',
  roleCreate: 'roles/create',
  users: 'users',
  userCreate: 'users/create',
  userEdit: 'users/edit/:id',
  user: 'users/:id',
  nodes: 'nodes',
  storeBase: 'store',
  storeHome: '',
  stores: 'choose',
  store: 'store',
  algorithmsManage: 'algorithms',
  algorithmCreate: 'algorithms/create',
  algorithmEdit: 'algorithms/edit/:id',
  algorithmManage: 'algorithms/:id',
  analyze: 'analyze',
  analyzeHome: '',
  tasks: 'tasks',
  taskCreate: 'tasks/create',
  taskCreateRepeat: 'tasks/create/repeat/:id',
  task: 'tasks/:id',
  algorithms: 'algorithms',
  algorithm: 'algorithms/:id/:algo_store_id',
  templateTaskCreate: 'template-tasks/create',
  storeUsers: 'users',
  storeUser: 'users/:id',
  storeUserCreate: 'users/create',
  storeUserEdit: 'users/edit/:id',
  storeRoles: 'roles',
  storeRole: 'roles/:id',
  storeRoleCreate: 'roles/create',
  storeRoleEdit: 'roles/edit/:id'
};
