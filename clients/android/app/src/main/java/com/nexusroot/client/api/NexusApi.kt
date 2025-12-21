package com.nexusroot.client.api

import com.nexusroot.client.models.*
import retrofit2.Response
import retrofit2.http.*

interface NexusApi {

    @POST("/api/register")
    suspend fun register(@Body request: RegisterRequest): Response<ApiResponse<Any>>

    @POST("/api/login")
    suspend fun login(@Body request: LoginRequest): Response<ApiResponse<LoginResponse>>

    @POST("/api/player/create")
    suspend fun createPlayer(@Body request: CreatePlayerRequest): Response<ApiResponse<Any>>

    @POST("/api/player/logout")
    suspend fun logout(@Body request: Map<String, String>): Response<ApiResponse<Any>>

    @POST("/api/command/execute")
    suspend fun executeCommand(
        @Header("Authorization") token: String?,
        @Body request: CommandRequest
    ): Response<ApiResponse<CommandResponse>>

    @GET("/api/player/{name}")
    suspend fun getPlayer(@Path("name") name: String): Response<ApiResponse<Player>>

    @GET("/api/status")
    suspend fun getStatus(): Response<ApiResponse<Any>>

    @GET("/api/leaderboard")
    suspend fun getLeaderboard(
        @Query("category") category: String = "level",
        @Query("limit") limit: Int = 10
    ): Response<ApiResponse<List<Player>>>

    @POST("/api/script/execute")
    suspend fun executeScript(@Body request: Map<String, String>): Response<ApiResponse<Any>>
}
