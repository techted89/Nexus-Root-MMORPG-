package com.nexusroot.client.models

data class ApiResponse<T>(
    val success: Boolean,
    val error: String? = null,
    val message: String? = null,
    val data: T? = null
)

data class LoginRequest(
    val username: String,
    val password: String
)

data class LoginResponse(
    val token: String? = null,
    val userId: String? = null
)

data class RegisterRequest(
    val username: String,
    val password: String
)

data class CreatePlayerRequest(
    val name: String,
    val is_vip: Boolean = false,
    val session_id: String? = null
)

data class CommandRequest(
    val command: String,
    val player_name: String? = null
)

data class CommandResponse(
    val output: String? = null,
    val animation_type: String = "TEXT_ONLY"
)

data class VirtualComputer(
    val heat: Float = 0f,
    val max_heat: Float = 100f,
    val cpu_tier: Int = 1,
    val ram_tier: Int = 1
)

data class Player(
    val name: String,
    val level: Int,
    val credits: Int,
    val experience: Int,
    val is_vip: Boolean,
    val wallet_address: String? = null,
    val virtual_computer: VirtualComputer? = null
)
