-- love_spatial_hash_pool.lua
-- Reference core systems for a survivors-like in LÖVE: a uniform spatial hash
-- (broad phase, avoids O(n^2)) + an object pool (no per-frame allocation), with
-- frame-independent updates. Drop in and adapt; this is the part that decides
-- whether you handle 50 entities or 5,000.

----------------------------------------------------------------------
-- Spatial hash: bucket entities into grid cells, only test nearby pairs.
-- Pick cell_size ~= the typical query/collision radius.
----------------------------------------------------------------------
local SpatialHash = {}
SpatialHash.__index = SpatialHash

function SpatialHash.new(cell_size)
	return setmetatable({ cell_size = cell_size, cells = {} }, SpatialHash)
end

local function key(cx, cy) return cx .. ":" .. cy end

function SpatialHash:_coords(x, y)
	return math.floor(x / self.cell_size), math.floor(y / self.cell_size)
end

function SpatialHash:clear()
	-- reuse cell tables where possible to avoid churn
	for _, bucket in pairs(self.cells) do
		for i = #bucket, 1, -1 do bucket[i] = nil end
	end
end

function SpatialHash:insert(e)
	local cx, cy = self:_coords(e.x, e.y)
	local k = key(cx, cy)
	local bucket = self.cells[k]
	if not bucket then bucket = {}; self.cells[k] = bucket end
	bucket[#bucket + 1] = e
end

-- Call fn(other) for every entity in the 3x3 block of cells around (x, y).
function SpatialHash:for_nearby(x, y, fn)
	local cx, cy = self:_coords(x, y)
	for ox = -1, 1 do
		for oy = -1, 1 do
			local bucket = self.cells[key(cx + ox, cy + oy)]
			if bucket then
				for i = 1, #bucket do fn(bucket[i]) end
			end
		end
	end
end

----------------------------------------------------------------------
-- Object pool: reuse instances instead of creating/collecting every frame.
----------------------------------------------------------------------
local Pool = {}
Pool.__index = Pool

function Pool.new(factory, reset)
	return setmetatable({ factory = factory, reset = reset, free = {}, active = {} }, Pool)
end

function Pool:acquire()
	local obj = table.remove(self.free) or self.factory()
	obj._alive = true
	self.active[#self.active + 1] = obj
	return obj
end

function Pool:release(obj)
	obj._alive = false           -- compacted out in update()
end

-- Compact the active list, returning dead objects to the free list.
function Pool:update()
	local active = self.active
	local n = 0
	for i = 1, #active do
		local obj = active[i]
		if obj._alive then
			n = n + 1
			active[n] = obj
		else
			if self.reset then self.reset(obj) end
			self.free[#self.free + 1] = obj
		end
	end
	for i = #active, n + 1, -1 do active[i] = nil end
end

----------------------------------------------------------------------
-- Example wiring: hundreds of projectiles vs. hundreds of enemies.
----------------------------------------------------------------------
local hash = SpatialHash.new(48)            -- ~ enemy/projectile size
local enemies = Pool.new(
	function() return { x = 0, y = 0, vx = 0, vy = 0, r = 12, hp = 3 } end)
local bullets = Pool.new(
	function() return { x = 0, y = 0, vx = 0, vy = 0, r = 4 } end)

function love.update(dt)               -- dt = seconds since last frame
	-- move bullets (frame-independent: everything * dt)
	for _, b in ipairs(bullets.active) do
		if b._alive then
			b.x = b.x + b.vx * dt
			b.y = b.y + b.vy * dt
		end
	end

	-- rebuild the hash from current enemy positions (broad phase)
	hash:clear()
	for _, e in ipairs(enemies.active) do
		if e._alive then hash:insert(e) end
	end

	-- narrow phase: each bullet only checks enemies in nearby cells, not all of them
	for _, b in ipairs(bullets.active) do
		if b._alive then
			hash:for_nearby(b.x, b.y, function(e)
				if e._alive and b._alive then
					local dx, dy = e.x - b.x, e.y - b.y
					local rr = e.r + b.r
					if dx * dx + dy * dy <= rr * rr then   -- circle overlap
						e.hp = e.hp - 1
						bullets:release(b)
						if e.hp <= 0 then enemies:release(e) end
					end
				end
			end)
		end
	end

	bullets:update()
	enemies:update()
end

return { SpatialHash = SpatialHash, Pool = Pool }
