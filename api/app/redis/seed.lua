-- Lua script to seed machines in Redis

local WASHER_DURATION = 1800
local DRYER_DURATION = 2400
local FLOORS = { 5, 8, 11, 14, 17 }

for _, floor in ipairs(FLOORS) do
	-- seed the washers
	for pos = 0, 1 do
		redis.call("JSON.SET", "machine"..":"..floor..":"..pos, ".", string.format(
			[[
			{
				"floor": %i,
				"pos": %i,
				"type": "washer",
				"status": "idle",
				"duration": %i,
				"last_started_at": "1970-01-01T00:00:00Z"
			}
			]], floor, pos, WASHER_DURATION
		))
	end
	-- and the dryers
	for pos = 2, 3 do
		redis.call("JSON.SET", "machine"..":"..floor..":"..pos, ".", string.format(
			[[
			{
				"floor": %i,
				"pos": %i,
				"type": "dryer",
				"status": "idle",
				"duration": %i,
				"last_started_at": "1970-01-01T00:00:00Z"
			}
			]], floor, pos, DRYER_DURATION
		))
	end
end
