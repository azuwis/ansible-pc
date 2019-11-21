local tohex = function(str)
  return str:gsub('.', function(c) return string.format('%02x', string.byte(c)) end)
end

local torrent = ngx.shared.torrent
local keys = torrent:get_keys(0)
ngx.say('info_hash                                report_uploaded,uploaded,downloaded,epoch,incomplete')
for _, info_hash in ipairs(keys) do
  ngx.say(tohex(info_hash) .. ' ' .. torrent:get(info_hash))
end
