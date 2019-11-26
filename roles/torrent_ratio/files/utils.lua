local M = {}

M.format = function(n)
  if n == 0 then
    return "0"
  end
  n = n / 1024
  if n < 1024 then
    return string.format('%.1fK', n)
  end
  n = n / 1024
  if n < 1024 then
    return string.format('%.1fM', n)
  end
  n = n / 1024
  return string.format('%.1fG', n)
end

M.tohex = function(str)
  return str:gsub('.', function(c) return string.format('%02x', string.byte(c)) end)
end

return M
