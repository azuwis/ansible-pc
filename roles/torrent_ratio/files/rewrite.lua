local format = function(n)
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

local random = function(range)
  local l, u = unpack(range)
  return l + math.random() * (u - l)
end

local tohex = function(str)
  return str:gsub('.', function(c) return string.format('%02x', string.byte(c)) end)
end

local tonum = function(str)
  return tonumber(str) or 0
end

local torrent = ngx.shared.torrent
local settings = require('settings')
settings = settings[ngx.var.host]
local args = ngx.req.get_uri_args()
local updown = ''
if settings ~= nil and type(args.uploaded) == 'string' and type(args.downloaded) == 'string' then
  if settings.https then
    ngx.var.tracker_scheme = 'https'
  end
  local uploaded = tonum(args.uploaded)
  local downloaded = tonum(args.downloaded)
  local epoch = ngx.time()
  local report_uploaded = uploaded
  local info = torrent:get(args.info_hash)
  if args.event ~= 'started' and info ~= nil then
    local previous_report_uploaded, previous_uploaded, previous_downloaded, previous_epoch, incomplete = string.match(info, '^(%d*),(%d*),(%d*),(%d*),(%d*)$')
    previous_report_uploaded = tonum(previous_report_uploaded)
    previous_uploaded = tonum(previous_uploaded)
    previous_downloaded = tonum(previous_downloaded)
    previous_epoch = tonum(previous_epoch)
    report_uploaded = previous_report_uploaded
    local delta_uploaded = uploaded - previous_uploaded
    report_uploaded = report_uploaded + delta_uploaded
    if tonum(incomplete) >= settings.incomplete then
      report_uploaded = report_uploaded + math.floor(delta_uploaded * random(settings.uploaded))
      report_uploaded = report_uploaded + math.floor((downloaded - previous_downloaded) * random(settings.downloaded))
      if math.random(100) <= settings.percent then
        report_uploaded = report_uploaded + math.floor((epoch - previous_epoch) * settings.speed * math.random())
      end
      -- args.left = 0
      -- args.downloaded = 0
    end
    args.uploaded = string.format('%d', report_uploaded)
  end
  torrent:set(args.info_hash, string.format('%d,%d,%d,%d,', report_uploaded, uploaded, downloaded, epoch), 10800)
  updown = string.format('hash: %s, up: %s/%s, down: %s,', tohex(args.info_hash), format(report_uploaded), format(uploaded), format(downloaded))
end
ngx.req.set_uri_args(args)
ngx.log(ngx.NOTICE, string.format('%s announce: "%s://%s%s%s%s"', updown, ngx.var.tracker_scheme, ngx.var.host, ngx.var.uri, ngx.var.is_args, ngx.var.args))
