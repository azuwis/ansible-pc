if ngx.header.content_encoding == "gzip" then
  local zlib = require "zlib"
  ngx.ctx.inflate = zlib.inflate()
end
