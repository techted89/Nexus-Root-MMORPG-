package com.nexusroot.client.viewmodel

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.nexusroot.client.models.*
import com.nexusroot.client.network.NetworkClient
import kotlinx.coroutines.launch
import retrofit2.Response

class MainViewModel : ViewModel() {

    private val _consoleOutput = MutableLiveData<String>()
    val consoleOutput: LiveData<String> = _consoleOutput

    private val _playerStats = MutableLiveData<Player?>()
    val playerStats: LiveData<Player?> = _playerStats

    private var sessionToken: String? = null
    private var playerName: String? = null

    init {
        appendOutput("Welcome to Nexus Root Mobile Client.")
        checkServerStatus()
    }

    private fun appendOutput(text: String) {
        val current = _consoleOutput.value ?: ""
        _consoleOutput.postValue("$current$text\n")
    }

    fun sendCommand(cmd: String) {
        if (cmd.isBlank()) return
        appendOutput("> $cmd")

        if (cmd.startsWith("login ")) {
            val parts = cmd.split(" ")
            if (parts.size == 3) {
                loginUser(parts[1], parts[2])
            } else {
                appendOutput("Usage: login <user> <pass>")
            }
            return
        }

        viewModelScope.launch {
            try {
                val token = sessionToken?.let { "Bearer $it" }
                val request = CommandRequest(cmd, playerName)

                val response = NetworkClient.api.executeCommand(token, request)
                handleCommandResponse(response)

                // Refresh stats after command (credits might have changed)
                if (playerName != null) {
                    refreshPlayerStats(playerName!!)
                }
            } catch (e: Exception) {
                appendOutput("Command Error: ${e.message}")
            }
        }
    }

    private fun handleCommandResponse(response: Response<ApiResponse<CommandResponse>>) {
        if (response.isSuccessful && response.body()?.success == true) {
            response.body()?.data?.output?.let { appendOutput(it) }
        } else {
            val error = response.body()?.error ?: response.message()
            appendOutput("Error: $error")
        }
    }

    private fun checkServerStatus() {
        appendOutput("Connecting to server...")
        viewModelScope.launch {
            try {
                val response = NetworkClient.api.getStatus()
                if (response.isSuccessful) {
                    appendOutput("Server Online.")
                    // Auto-login for demo convenience
                    loginUser("android_user", "password123")
                } else {
                    appendOutput("Server Error: ${response.code()}")
                }
            } catch (e: Exception) {
                appendOutput("Connection Failed: ${e.message}")
                appendOutput("Ensure server is running on http://10.0.2.2:8080")
            }
        }
    }

    private fun loginUser(user: String, pass: String) {
        viewModelScope.launch {
            try {
                val request = LoginRequest(user, pass)
                val response = NetworkClient.api.login(request)

                if (response.isSuccessful && response.body()?.success == true) {
                    sessionToken = response.body()?.data?.token
                    playerName = user
                    appendOutput("Logged in as $user")
                    createPlayerIfNeeded(user)
                    refreshPlayerStats(user)
                } else {
                    appendOutput("Login failed. Attempting registration...")
                    registerUser(user, pass)
                }
            } catch (e: Exception) {
                appendOutput("Login Error: ${e.message}")
            }
        }
    }

    private fun registerUser(user: String, pass: String) {
        viewModelScope.launch {
            try {
                val request = RegisterRequest(user, pass)
                val response = NetworkClient.api.register(request)

                if (response.isSuccessful && response.body()?.success == true) {
                    appendOutput("Registration successful. Logging in...")
                    // Recursively call login
                    val loginRequest = LoginRequest(user, pass)
                    val loginResponse = NetworkClient.api.login(loginRequest)
                     if (loginResponse.isSuccessful && loginResponse.body()?.success == true) {
                        sessionToken = loginResponse.body()?.data?.token
                        playerName = user
                        appendOutput("Logged in as $user")
                        createPlayerIfNeeded(user)
                        refreshPlayerStats(user)
                     }
                } else {
                    appendOutput("Registration failed: ${response.body()?.error}")
                }
            } catch (e: Exception) {
                appendOutput("Registration Error: ${e.message}")
            }
        }
    }

    private suspend fun createPlayerIfNeeded(name: String) {
        try {
            val request = CreatePlayerRequest(name)
            NetworkClient.api.createPlayer(request)
        } catch (e: Exception) {
            // Ignore
        }
    }

    private suspend fun refreshPlayerStats(name: String) {
        try {
            val response = NetworkClient.api.getPlayer(name)
            if (response.isSuccessful && response.body()?.success == true) {
                val player = response.body()?.data
                if (player != null) {
                    _playerStats.postValue(player)
                }
            }
        } catch (e: Exception) {
            // Silently fail for stats refresh
        }
    }
}
