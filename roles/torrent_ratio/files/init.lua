local torrent = ngx.shared.torrent

local file = io.open('/var/lib/nginx/torrent_ratio')
if file ~= nil then
  for line in file:lines() do
    local info_hash, info = string.match(line, '^([0-9a-f]+) ([0-9,]+)$')
    if info_hash ~= nil and info ~= nil then
      torrent:set(info_hash, info, 10800)
    end
  end
  file:close()
end

