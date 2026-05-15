/**
 * PX4 安全检测报告 - 前端交互脚本
 */

const API_BASE = '/api';
let currentReport = 'agent4';

/**
 * 页面加载完成后的初始化
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('页面加载完成，初始化中...');
    
    // 绑定按钮事件
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const reportId = this.dataset.report;
            loadReport(reportId);
        });
    });
    
    // 加载初始报告（综合报告）
    loadReport('agent4');
    
    // 更新页脚时间
    updateFooterTime();
});

/**
 * 加载指定的报告
 */
async function loadReport(reportId) {
    console.log(`加载报告: ${reportId}`);
    
    // 更新按钮状态
    updateActiveButton(reportId);
    currentReport = reportId;
    
    // 显示加载状态
    showLoading();
    hideError();
    
    try {
        // 调用 API 获取报告内容
        const response = await fetch(`${API_BASE}/report/${reportId}`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        // 显示报告内容
        displayReport(data);
        hideLoading();
        
    } catch (error) {
        console.error('加载失败:', error);
        showError(`加载失败: ${error.message}`);
        hideLoading();
    }
}

/**
 * 显示报告内容
 */
function displayReport(data) {
    // 隐藏报告头部（信息移到内容里）
    const header = document.getElementById('report-header');
    header.classList.add('hidden');
    
    // 处理和显示内容
    const content = data.content;
    const htmlContent = markdownToHtml(content, data);
    
    const contentDiv = document.getElementById('report-content');
    contentDiv.innerHTML = htmlContent;
    
    // 代码高亮和功能绑定
    highlightAndEnhanceCode();
    
    // 滚动到顶部
    window.scrollTo(0, 0);
}

/**
 * 代码高亮和增强功能（复制按钮等）
 */
function highlightAndEnhanceCode() {
    // 对所有代码块进行高亮处理
    document.querySelectorAll('pre code').forEach((codeBlock) => {
        // 应用 Highlight.js 高亮
        if (window.hljs) {
            hljs.highlightElement(codeBlock);
        }
    });
    
    // 为复制按钮添加事件监听
    document.querySelectorAll('.code-copy-btn').forEach((btn) => {
        btn.addEventListener('click', function() {
            const codeBlock = this.closest('.code-block').querySelector('code');
            const code = codeBlock.textContent;
            
            // 复制到剪贴板
            navigator.clipboard.writeText(code).then(() => {
                // 显示复制成功反馈
                const originalText = this.textContent;
                this.textContent = 'Copied';
                this.classList.add('copied');
                
                // 2秒后恢复原文本
                setTimeout(() => {
                    this.textContent = originalText;
                    this.classList.remove('copied');
                }, 2000);
            }).catch(() => {
                alert('Copy failed. Please copy manually.');
            });
        });
    });
}

/**
 * 简易 Markdown 转 HTML 转换
 */
function markdownToHtml(markdown, data) {
    let html = markdown;
    
    // 删除分隔线 "---"
    html = html.replace(/^---+$/gm, '');
    html = html.replace(/\n\n\n+/g, '\n\n');  // 清理多余空行
    
    // 【第一步 - 关键】先提取代码块，用占位符替换，保护代码块内容不被转义破坏
    const codeBlockMap = {};
    let codeBlockIndex = 0;
    
    html = html.replace(/```([a-z0-9]*)\n([\s\S]*?)```/g, function(match, lang, code) {
        // 只删除首尾换行符，保留所有内部缩进
        code = code.replace(/^\n+|\n+$/g, '');
        const language = lang || 'plaintext';
        
        // 保存代码块到 map，用唯一占位符替换
        const placeholder = 'CODEBLOCK' + codeBlockIndex;
        codeBlockMap[placeholder] = {
            lang: language,
            code: code
        };
        codeBlockIndex++;
        
        return placeholder;
    });
    
    // 【第二步】提取 Agent Report 链接并用占位符替换
    const agentLinkMap = {};
    let placeholderIndex = 0;
    
    html = html.replace(/agent([1-4])_?report\.md/gi, function(match) {
        const agentNum = match.match(/\d/)[0];
        const reportMap = {
            '1': 'agent1',
            '2': 'agent2',
            '3': 'agent3',
            '4': 'agent4'
        };
        const reportId = reportMap[agentNum];
        const reportNames = {
            '1': '漏洞分析',
            '2': '代码扫描',
            '3': '仿真验证',
            '4': '综合报告'
        };
        
        const placeholderId = 'AGENTLINK' + placeholderIndex;
        agentLinkMap[placeholderId] = {
            reportId: reportId,
            reportName: reportNames[agentNum],
            originalText: match
        };
        placeholderIndex++;
        
        return placeholderId;
    });
    
    // 【第三步】现在转义 HTML 特殊字符（代码块已经被保护）
    html = html
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
    
    // 标题：# ## ###
    html = html.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.*?)$/gm, function(match, title) {
        // 在第一个h1标题后面插入文件信息
        if (html.indexOf(match) === html.lastIndexOf(match)) {
            // 只有一个h1标题时
            return match + '<div class="report-meta-info"><p>文件: ' + (data ? data.file_path : '') + '</p>' +
                   '<p>大小: ' + (data ? formatFileSize(data.file_size) : '') + '</p>' +
                   '<p>报告生成时间: ' + (data ? formatDateTime(data.modified_time) : '') + '</p></div>';
        }
        return match;
    });
    
    // 内联代码：`code`
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // 加粗：**text** 或 __text__
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/__([^_]+)__/g, '<strong>$1</strong>');
    
    // 斜体：*text* 或 _text_
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    html = html.replace(/_([^_]+)_/g, '<em>$1</em>');
    
    // 链接：[text](url)
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
    
    // 引用块：> text
    html = html.replace(/^&gt; (.*?)$/gm, '<blockquote>$1</blockquote>');
    
    // 表格处理
    html = html.replace(/(\|.+\n)+/g, function(table) {
        const rows = table.trim().split('\n');
        let htmlTable = '<table><thead><tr>';
        
        // 表头
        const headerCells = rows[0].split('|').filter(cell => cell.trim());
        headerCells.forEach(cell => {
            htmlTable += '<th>' + cell.trim() + '</th>';
        });
        htmlTable += '</tr></thead><tbody>';
        
        // 跳过分隔符行，处理数据行
        for (let i = 2; i < rows.length; i++) {
            const cells = rows[i].split('|').filter(cell => cell.trim());
            if (cells.length > 0) {
                htmlTable += '<tr>';
                cells.forEach(cell => {
                    htmlTable += '<td>' + cell.trim() + '</td>';
                });
                htmlTable += '</tr>';
            }
        }
        
        htmlTable += '</tbody></table>';
        return htmlTable;
    });
    
    // 有序列表：1. 2. 3.
    html = html.replace(/^\d+\. (.*?)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*?<\/li>)/s, '<ol>$1</ol>');
    
    // 无序列表：- 或 *
    html = html.replace(/^[-*] (.*?)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*?<\/li>)/s, function(match) {
        if (!match.includes('<ol>')) {
            return '<ul>' + match + '</ul>';
        }
        return match;
    });
    
    // 换行：\n\n -> <p>
    html = html.replace(/\n\n+/g, '</p><p>');
    html = '<p>' + html + '</p>';
    
    // 清理多余的 p 标签
    html = html.replace(/<p><\/p>/g, '');
    html = html.replace(/<p>(<h[1-6])/g, '$1');
    html = html.replace(/(<\/h[1-6]>)<\/p>/g, '$1');
    html = html.replace(/<p>(<ul>|<ol>|<table>|<pre>|<blockquote>|<div)/g, '$1');
    html = html.replace(/(<\/ul>|<\/ol>|<\/table>|<\/pre>|<\/blockquote>|<\/div>)<\/p>/g, '$1');
    
    // 【第四步 - 关键】恢复所有代码块占位符为真实的代码块 HTML
    for (const [placeholder, codeBlockData] of Object.entries(codeBlockMap)) {
        const { lang, code } = codeBlockData;
        
        // HTML 转义处理代码内容
        const escapedCode = code
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
        
        // 生成代码块 HTML
        let codeBlockHtml = '<div class="code-block">';
        codeBlockHtml += '<div class="code-header">';
        codeBlockHtml += '<span class="code-lang">' + lang + '</span>';
        codeBlockHtml += '<button class="code-copy-btn" title="Copy">Copy</button>';
        codeBlockHtml += '</div>';
        codeBlockHtml += '<pre><code class="language-' + lang + '" data-language="' + lang + '">' + escapedCode + '</code></pre>';
        codeBlockHtml += '</div>';
        
        // 用正则表达式进行全局替换（确保替换所有占位符）
        const regex = new RegExp(placeholder, 'g');
        html = html.replace(regex, codeBlockHtml);
    }
    
    // 【第五步】将所有占位符替换为实际的链接 HTML
    // 使用正则表达式全局替换（更可靠）
    for (const [placeholderId, linkInfo] of Object.entries(agentLinkMap)) {
        const linkHtml = '<a href="#" class="agent-report-link" data-report="' + linkInfo.reportId + '" title="点击跳转到' + linkInfo.reportName + '">' + linkInfo.originalText + '</a>';
        // 用正则表达式进行全局替换
        const regex = new RegExp(placeholderId, 'g');
        html = html.replace(regex, linkHtml);
    }
    
    // 完成转换后，为 agent report 链接添加点击事件监听
    setTimeout(function() {
        const links = document.querySelectorAll('.agent-report-link');
        links.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const reportId = this.getAttribute('data-report');
                loadReport(reportId);
            });
        });
    }, 0);
    
    return html;
}

/**
 * 更新活跃按钮状态
 */
function updateActiveButton(reportId) {
    const buttons = document.querySelectorAll('.nav-btn');
    buttons.forEach(btn => {
        if (btn.dataset.report === reportId) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

/**
 * 显示加载状态
 */
function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

/**
 * 隐藏加载状态
 */
function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

/**
 * 显示错误信息
 */
function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
}

/**
 * 隐藏错误信息
 */
function hideError() {
    document.getElementById('error').classList.add('hidden');
}

/**
 * 格式化文件大小
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    
    const units = ['B', 'KB', 'MB', 'GB'];
    const k = 1024;
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + units[i];
}

/**
 * 格式化日期时间
 */
function formatDateTime(isoString) {
    try {
        const date = new Date(isoString);
        return date.toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    } catch (e) {
        return isoString;
    }
}

/**
 * 更新页脚时间戳
 */
function updateFooterTime() {
    const now = new Date();
    const timeStr = now.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
    document.getElementById('timestamp').textContent = timeStr;
}

// 每分钟更新一次页脚时间
setInterval(updateFooterTime, 60000);

console.log('✅ 脚本加载完成');
