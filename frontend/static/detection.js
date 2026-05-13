// DOM 元素获取
const welcomeScreen = document.getElementById('welcomeScreen');
const uavFormScreen = document.getElementById('uavFormScreen');
const processingScreen = document.getElementById('processingScreen');

const uavBtn = document.querySelector('[data-type="uav"]');
const drivingBtn = document.querySelector('[data-type="driving"]');
const robotBtn = document.querySelector('[data-type="robot"]');
const backBtn = document.getElementById('backBtn');

const dropZone = document.getElementById('dropZone');
const fileUpload = document.getElementById('fileUpload');
const uavForm = document.getElementById('uavForm');
const submitBtn = document.getElementById('submitBtn');

let selectedFile = null;
let selectedCountry = null;

// ===== 屏幕切换函数 =====
function showScreen(screenName) {
    welcomeScreen.classList.remove('active');
    uavFormScreen.classList.remove('active');
    processingScreen.classList.remove('active');

    if (screenName === 'welcome') {
        welcomeScreen.classList.add('active');
    } else if (screenName === 'uavForm') {
        uavFormScreen.classList.add('active');
    } else if (screenName === 'processing') {
        processingScreen.classList.add('active');
    }
}

// ===== 选项按钮事件 =====
uavBtn.addEventListener('click', () => {
    showScreen('uavForm');
});

drivingBtn.addEventListener('click', () => {
    alert('智能驾驶软件检测功能开发中...');
});

robotBtn.addEventListener('click', () => {
    alert('机器人软件检测功能开发中...');
});

// ===== 返回按钮 =====
backBtn.addEventListener('click', () => {
    selectedFile = null;
    selectedCountry = null;
    
    const uploadContainer = document.getElementById('uploadContainer');
    const readingSuccess = document.getElementById('readingSuccess');
    const readingProgress = document.getElementById('readingProgress');
    
    uploadContainer.style.display = 'block';
    readingSuccess.style.display = 'none';
    readingProgress.style.display = 'none';
    
    fileUpload.value = '';
    document.getElementById('countrySelect').value = '';
    submitBtn.disabled = false;
    
    showScreen('welcome');
});

// ===== 文件上传处理 =====
// 点击上传区域时触发文件选择
dropZone.addEventListener('click', () => {
    fileUpload.click();
});

// 文件选择改变
fileUpload.addEventListener('change', (e) => {
    handleFileSelect(e.target.files);
});

// 拖拽事件处理
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropZone.classList.remove('dragover');
    handleFileSelect(e.dataTransfer.files);
});

// 处理文件选择
function handleFileSelect(files) {
    if (files.length > 0) {
        const file = files[0];
        
        // 检查是否是 ZIP 文件
        if (file.type === 'application/zip' || file.name.endsWith('.zip')) {
            selectedFile = file;
            
            // 显示读取进度条
            showFileReadingProgress(file.name);
        } else {
            alert('请上传 ZIP 文件！');
            selectedFile = null;
        }
    }
}

// 显示文件读取进度条（3秒）
function showFileReadingProgress(fileName) {
    const uploadContainer = document.getElementById('uploadContainer');
    const readingProgress = document.getElementById('readingProgress');
    const readingFill = document.getElementById('readingFill');
    const readingPercentage = document.getElementById('readingPercentage');
    const readingSuccess = document.getElementById('readingSuccess');
    const successFileName = document.getElementById('successFileName');
    
    // 隐藏上传区域，显示读取进度
    uploadContainer.style.display = 'none';
    readingProgress.style.display = 'block';
    readingSuccess.style.display = 'none';
    
    // 重置进度条
    readingFill.style.width = '0%';
    readingPercentage.textContent = '0%';
    
    const totalDuration = 3000; // 3秒
    const startTime = Date.now();
    
    function updateReading() {
        const now = Date.now();
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / totalDuration, 1);
        
        const percent = Math.floor(progress * 100);
        readingFill.style.width = percent + '%';
        readingPercentage.textContent = percent + '%';
        
        if (elapsed < totalDuration) {
            requestAnimationFrame(updateReading);
        } else {
            // 读取完成
            readingFill.style.width = '100%';
            readingPercentage.textContent = '100%';
            
            // 1秒后显示成功信息
            setTimeout(() => {
                readingProgress.style.display = 'none';
                readingSuccess.style.display = 'block';
                successFileName.textContent = fileName;
            }, 500);
        }
    }
    
    updateReading();
}

// 更换文件按钮
document.addEventListener('DOMContentLoaded', () => {
    const changeFileBtn = document.getElementById('changeFileBtn');
    if (changeFileBtn) {
        changeFileBtn.addEventListener('click', () => {
            selectedFile = null;
            const uploadContainer = document.getElementById('uploadContainer');
            const readingSuccess = document.getElementById('readingSuccess');
            
            uploadContainer.style.display = 'block';
            readingSuccess.style.display = 'none';
            fileUpload.value = '';
        });
    }
});

// ===== 表单提交 =====
uavForm.addEventListener('submit', (e) => {
    e.preventDefault();

    // 获取表单值
    const countrySelect = document.getElementById('countrySelect');
    selectedCountry = countrySelect.value;

    // 验证表单
    if (!selectedCountry) {
        alert('请选择国家！');
        return;
    }

    if (!selectedFile) {
        alert('请上传 ZIP 文件！');
        return;
    }

    // 禁用提交按钮
    submitBtn.disabled = true;
    
    // 显示处理中界面
    showScreen('processing');
    
    // 启动进度条动画
    startProgressAnimation();
});

// ===== Easing 函数 =====
// easeInQuad: 先慢后快（加速度增加）
function easeInQuad(t) {
    return t * t;
}

// ===== 时间映射函数：按不同速度显示进度，但保证最终100%与真实结束同步 =====
function getVisualElapsed(elapsed, totalDuration) {
    const segments = [
        { startPercent: 0, endPercent: 5, speedMultiplier: 1.0 },      // 解压缩前5%
        { startPercent: 5, endPercent: 10, speedMultiplier: 5.0 },     // 解压缩5-10%快一倍以上
        { startPercent: 10, endPercent: 50, speedMultiplier: 1.0 },    // 解压缩后半部分+分析
        { startPercent: 50, endPercent: 67, speedMultiplier: 0.1 },    // Agent3执行慢一倍
        { startPercent: 67, endPercent: 85, speedMultiplier: 1.0 },    // 生成报告前半部分
        { startPercent: 85, endPercent: 90, speedMultiplier: 5.0 },     // 生成报告中快一倍
        { startPercent: 90, endPercent: 100, speedMultiplier: 10.0 }    // 生成报告最后加速
    ];

    const segmentInfo = segments.map((segment) => {
        const realStart = (totalDuration * segment.startPercent) / 100;
        const realEnd = (totalDuration * segment.endPercent) / 100;
        const realDuration = realEnd - realStart;
        const visualDuration = realDuration * segment.speedMultiplier;

        return {
            ...segment,
            realStart,
            realEnd,
            realDuration,
            visualDuration
        };
    });

    const totalVisualDuration = segmentInfo.reduce((sum, segment) => sum + segment.visualDuration, 0);
    let visualElapsed = 0;

    for (let i = 0; i < segmentInfo.length; i++) {
        const segment = segmentInfo[i];

        if (elapsed <= segment.realStart) {
            break;
        }

        if (elapsed >= segment.realEnd) {
            visualElapsed += segment.visualDuration;
        } else {
            const realElapsedInSegment = elapsed - segment.realStart;
            visualElapsed += realElapsedInSegment * segment.speedMultiplier;
            break;
        }
    }

    return (visualElapsed / totalVisualDuration) * totalDuration;
}

// easeOutQuad: 先快后慢（减速度）
function easeOutQuad(t) {
    return 1 - (1 - t) * (1 - t);
}

// ===== 进度条动画 =====
function startProgressAnimation() {
    const progressFill = document.getElementById('progressFill');
    const progressPercentage = document.getElementById('progressPercentage');
    const agentWorkflow = document.getElementById('agentWorkflow');
    
    const steps = [
        { id: 'step1', duration: 5000, pauseAfter: 800 },        // 解压缩 ZIP 包 - 5s + 暂停
        { id: 'step2', duration: 5000, pauseAfter: 800 },        // 分析代码结构 - 5s + 暂停
        { id: 'step3', duration: 20000, pauseAfter: 800, agents: true }, // 执行安全检测 - 20s + 暂停 + Agent动画
        { id: 'step4', duration: 10000, pauseAfter: 0 }          // 生成检测报告 - 10s
    ];
    
    let currentPercent = 0;
    let cumulativeTime = 0;
    const stepTimings = [];
    
    // 计算总时长（包含暂停时间）
    let totalDuration = 0;
    for (let i = 0; i < steps.length; i++) {
        totalDuration += steps[i].duration + steps[i].pauseAfter;
    }
    
    // 计算每个步骤的时间段
    for (let i = 0; i < steps.length; i++) {
        stepTimings.push({
            id: steps[i].id,
            duration: steps[i].duration,
            startTime: cumulativeTime,
            endTime: cumulativeTime + steps[i].duration,
            pauseStart: cumulativeTime + steps[i].duration,
            pauseEnd: cumulativeTime + steps[i].duration + steps[i].pauseAfter,
            hasAgents: steps[i].agents || false
        });
        cumulativeTime += steps[i].duration + steps[i].pauseAfter;
    }
    
    const startTime = Date.now();
    
    // 重置所有步骤
    document.querySelectorAll('.step').forEach(step => {
        step.classList.remove('active', 'completed');
        step.querySelector('.step-icon').textContent = '⏳';
    });
    
    // 隐藏 Agent 工作流
    if (agentWorkflow) {
        agentWorkflow.style.display = 'none';
    }
    
    function updateProgress() {
        const now = Date.now();
        const realElapsed = now - startTime;
        const displayedElapsed = getVisualElapsed(realElapsed, totalDuration);
        const progress = Math.min(displayedElapsed / totalDuration, 1);
        
        // 计算实际百分比（基于总时长）
        currentPercent = Math.floor(progress * 100);
        progressFill.style.width = currentPercent + '%';
        progressPercentage.textContent = currentPercent + '%';
        
        // 更新步骤状态
        for (let i = 0; i < stepTimings.length; i++) {
            const timing = stepTimings[i];
            const stepElement = document.getElementById(timing.id);
            if (!stepElement) continue;
            
            if (realElapsed < timing.startTime) {
                // 未开始
                stepElement.classList.remove('active', 'completed');
                stepElement.querySelector('.step-icon').textContent = '⏳';
                // 隐藏 Agent 工作流
                if (agentWorkflow && timing.hasAgents) {
                    agentWorkflow.style.display = 'none';
                }
            } else if (realElapsed < timing.endTime) {
                // 正在进行 - 使用 easing 函数计算本步骤内的进度
                const stepElapsed = realElapsed - timing.startTime;
                const stepProgress = stepElapsed / timing.duration;
                const easedProgress = easeInQuad(stepProgress); // 先慢后快
                
                stepElement.classList.add('active');
                stepElement.classList.remove('completed');
                stepElement.querySelector('.step-icon').textContent = '⏳';
                
                // 显示 Agent 工作流
                if (agentWorkflow && timing.hasAgents) {
                    agentWorkflow.style.display = 'flex';
                    updateAgentWorkflow(easedProgress);
                }
            } else if (realElapsed < timing.pauseEnd) {
                // 暂停中（节点完成但继续显示）
                stepElement.classList.add('completed');
                stepElement.classList.remove('active');
                stepElement.querySelector('.step-icon').textContent = '✓';
                
                // 如果是step3，在暂停时隐藏Agent工作流
                if (agentWorkflow && timing.hasAgents) {
                    agentWorkflow.style.display = 'flex';
                    // 所有Agent都标记为完成
                    document.querySelectorAll('.agent-item').forEach(item => {
                        item.classList.add('completed');
                        item.classList.remove('active');
                    });
                }
            } else {
                // 已完成且暂停结束
                stepElement.classList.add('completed');
                stepElement.classList.remove('active');
                stepElement.querySelector('.step-icon').textContent = '✓';
                
                // 隐藏 Agent 工作流
                if (agentWorkflow && timing.hasAgents) {
                    agentWorkflow.style.display = 'none';
                }
            }
        }
        
        if (realElapsed < totalDuration) {
            requestAnimationFrame(updateProgress);
        } else {
            // 完成
            progressFill.style.width = '100%';
            progressPercentage.textContent = '100%';
            document.querySelectorAll('.step').forEach(step => {
                step.classList.add('completed');
                step.classList.remove('active');
                step.querySelector('.step-icon').textContent = '✓';
            });
            if (agentWorkflow) {
                agentWorkflow.style.display = 'none';
            }
            
            // 2秒后跳转到报告页面
            setTimeout(() => {
                window.location.href = '/reports';
            }, 2000);
        }
    }
    
    updateProgress();
}

// 更新 Agent 工作流显示
function updateAgentWorkflow(progress) {
    const agents = ['agent1Work', 'agent2Work', 'agent3Work'];
    const agentsPerSection = 1 / agents.length;
    
    for (let i = 0; i < agents.length; i++) {
        const agentElement = document.getElementById(agents[i]);
        if (!agentElement) continue;
        
        const agentStartProgress = i * agentsPerSection;
        const agentEndProgress = (i + 1) * agentsPerSection;
        
        if (progress < agentStartProgress) {
            // 未开始
            agentElement.classList.remove('active', 'completed');
        } else if (progress < agentEndProgress) {
            // 正在进行
            agentElement.classList.add('active');
            agentElement.classList.remove('completed');
        } else {
            // 已完成
            agentElement.classList.add('completed');
            agentElement.classList.remove('active');
        }
    }
}

// 返回按钮（处理中界面）
document.addEventListener('DOMContentLoaded', () => {
    const backBtn2 = document.getElementById('backBtn2');
    if (backBtn2) {
        backBtn2.addEventListener('click', () => {
            selectedFile = null;
            selectedCountry = null;
            
            const uploadContainer = document.getElementById('uploadContainer');
            const readingSuccess = document.getElementById('readingSuccess');
            const readingProgress = document.getElementById('readingProgress');
            
            uploadContainer.style.display = 'block';
            readingSuccess.style.display = 'none';
            readingProgress.style.display = 'none';
            
            fileUpload.value = '';
            document.getElementById('countrySelect').value = '';
            submitBtn.disabled = false;
            
            showScreen('uavForm');
        });
    }
});

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', () => {
    showScreen('welcome');
});
