local settings = require('settings')
settings = settings[ngx.var.host]
if settings == nil then
  return
end

local inflate = ngx.ctx.inflate
local chunk = ngx.arg[1]
if inflate and chunk ~= "" then
  local eof
  chunk, eof = inflate(chunk)
end

if chunk ~= "" then
  -- ngx.log(ngx.INFO, 'chunk: "' .. chunk .. '"')
  local match = string.match(chunk, '10:incompletei(%d+)e')
  if (match) then
    incomplete = tonumber(match)
    local torrent = ngx.shared.torrent
    local args = ngx.req.get_uri_args()
    local info = torrent:get(args.info_hash)
    torrent:set(args.info_hash, info .. incomplete)
  end
end
