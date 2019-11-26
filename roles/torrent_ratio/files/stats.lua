local utils = require('utils')

local function format(str)
  return utils.format(tonumber(str))
end

local torrent = ngx.shared.torrent
local args = ngx.req.get_uri_args()
local keys = torrent:get_keys(0)
local current_epoch = ngx.time()
ngx.say('info_hash                                report_uploaded,uploaded,downloaded,epoch,incomplete')
for _, info_hash in ipairs(keys) do
  local info = torrent:get(info_hash)
  if not args.raw then
    local report_uploaded, uploaded, downloaded, epoch, incomplete = string.match(info, '^(%d*),(%d*),(%d*),(%d*),(%d*)$')
    info = string.format('% 15s % 8s % 10s % 4sm % 10s', format(report_uploaded), format(uploaded), format(downloaded), math.floor((current_epoch - epoch) / 60), incomplete)
  end
  ngx.say(utils.tohex(info_hash) .. ' ' .. info)
end
