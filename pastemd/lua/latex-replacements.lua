-- 修复不兼容的 LaTeX 语法
-- 在 Math 节点中应用替换规则，处理 Pandoc 不支持的 LaTeX 命令

-- 替换规则列表
local replacements = {
  -- 将 {\kern 10pt} 或 \kern 10pt 替换为 \qquad
  { pattern = "{\\kern%s+%d+pt}", replacement = "\\qquad" },
  { pattern = "\\kern%s+%d+pt",  replacement = "\\qquad" },
  -- 可以在这里添加更多规则
}

local function latex_replacements(math_content)
  local result = math_content
  
  -- 应用所有替换规则
  for _, rule in ipairs(replacements) do
    result = result:gsub(rule.pattern, rule.replacement)
  end
  
  return result
end

local function process_math(el)
  -- 处理 Math 元素（行内公式和块级公式）
  el.text = latex_replacements(el.text)
  return el
end

return {
  {
    Math = process_math
  }
}
