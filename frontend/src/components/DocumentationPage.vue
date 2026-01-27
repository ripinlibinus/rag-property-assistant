<template>
  <!-- DocumentationPage Component -->
  <div class="h-full flex flex-col md:flex-row">
    <!-- Mobile Section Navigation Toggle -->
    <div class="md:hidden border-b bg-gray-50 px-4 py-3 flex items-center justify-between">
      <button
        @click="showMobileNav = !showMobileNav"
        class="flex items-center gap-2 text-gray-700"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
        </svg>
        <span class="font-medium">{{ sections.find(s => s.id === activeSection)?.title }}</span>
      </button>
      <button
        @click="$emit('back-to-chat')"
        class="text-sm text-blue-600 hover:text-blue-700 font-medium"
      >
        Back to Chat
      </button>
    </div>

    <!-- Mobile Navigation Dropdown -->
    <div
      v-if="showMobileNav"
      class="md:hidden absolute left-0 right-0 top-[calc(3.5rem+49px)] bg-white border-b shadow-lg z-30"
    >
      <nav class="py-2">
        <button
          v-for="section in sections"
          :key="section.id"
          @click="activeSection = section.id; showMobileNav = false"
          class="w-full px-4 py-3 text-left flex items-center gap-3 hover:bg-gray-50"
          :class="activeSection === section.id ? 'bg-blue-50 text-blue-700' : 'text-gray-700'"
        >
          <span v-html="section.icon" class="w-5 h-5"></span>
          <span>{{ section.title }}</span>
        </button>
      </nav>
    </div>

    <!-- Desktop Sidebar Navigation -->
    <aside class="hidden md:flex w-64 flex-shrink-0 flex-col border-r bg-gray-50">
      <div class="p-4 border-b">
        <button
          @click="$emit('back-to-chat')"
          class="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium text-sm"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
          </svg>
          Back to Chat
        </button>
      </div>
      <nav class="flex-1 overflow-y-auto py-4">
        <button
          v-for="section in sections"
          :key="section.id"
          @click="activeSection = section.id"
          class="w-full px-4 py-2.5 text-left flex items-center gap-3 hover:bg-gray-100 transition-colors"
          :class="activeSection === section.id ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-600' : 'text-gray-600'"
        >
          <span v-html="section.icon" class="w-5 h-5 flex-shrink-0"></span>
          <span class="text-sm font-medium">{{ section.title }}</span>
        </button>
      </nav>
    </aside>

    <!-- Content Area -->
    <main class="flex-1 overflow-y-auto">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- System Overview -->
        <section v-if="activeSection === 'overview'" class="space-y-8">
          <div>
            <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 mb-4">System Overview</h1>
            <p class="text-gray-600 leading-relaxed">
              RAG Property Search is a property search system based on Retrieval-Augmented Generation (RAG) that combines the power of Large Language Models with structured data search and semantic search capabilities.
            </p>
          </div>

          <!-- Architecture Diagram -->
          <div class="bg-gray-50 rounded-xl p-6">
            <h2 class="text-lg font-semibold text-gray-800 mb-4">Architecture</h2>
            <div class="bg-white rounded-lg p-4 border">
              <div class="flex flex-col items-center space-y-4">
                <!-- User -->
                <div class="bg-blue-100 text-blue-800 px-4 py-2 rounded-lg font-medium">User Query</div>
                <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path></svg>
                <!-- Agent -->
                <div class="bg-emerald-100 text-emerald-800 px-4 py-2 rounded-lg font-medium">ReAct Agent (GPT-4)</div>
                <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path></svg>
                <!-- Tools -->
                <div class="flex flex-wrap justify-center gap-2">
                  <span class="bg-purple-100 text-purple-800 px-3 py-1 rounded text-sm">Property API</span>
                  <span class="bg-amber-100 text-amber-800 px-3 py-1 rounded text-sm">ChromaDB</span>
                  <span class="bg-pink-100 text-pink-800 px-3 py-1 rounded text-sm">Geocoding</span>
                  <span class="bg-cyan-100 text-cyan-800 px-3 py-1 rounded text-sm">Reranker</span>
                </div>
                <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path></svg>
                <!-- Response -->
                <div class="bg-blue-100 text-blue-800 px-4 py-2 rounded-lg font-medium">Generated Response</div>
              </div>
            </div>
          </div>

          <!-- Tech Stack -->
          <div>
            <h2 class="text-lg font-semibold text-gray-800 mb-4">Tech Stack</h2>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div class="bg-white border rounded-lg p-4 text-center">
                <div class="text-2xl mb-2">Vue 3</div>
                <div class="text-sm text-gray-500">Frontend</div>
              </div>
              <div class="bg-white border rounded-lg p-4 text-center">
                <div class="text-2xl mb-2">FastAPI</div>
                <div class="text-sm text-gray-500">Backend</div>
              </div>
              <div class="bg-white border rounded-lg p-4 text-center">
                <div class="text-2xl mb-2">ChromaDB</div>
                <div class="text-sm text-gray-500">Vector Store</div>
              </div>
              <div class="bg-white border rounded-lg p-4 text-center">
                <div class="text-2xl mb-2">OpenAI</div>
                <div class="text-sm text-gray-500">LLM Provider</div>
              </div>
            </div>
          </div>
        </section>

        <!-- Search Methods -->
        <section v-else-if="activeSection === 'methods'" class="space-y-8">
          <div>
            <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 mb-4">Search Methods</h1>
            <p class="text-gray-600 leading-relaxed">
              This system provides three search methods that can be selected based on your needs.
            </p>
          </div>

          <!-- Method Cards -->
          <div class="space-y-6">
            <!-- Hybrid -->
            <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200">
              <div class="flex items-center gap-3 mb-4">
                <span class="bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-medium">Recommended</span>
                <h2 class="text-xl font-semibold text-gray-800">Hybrid Search</h2>
              </div>
              <p class="text-gray-600 mb-4">
                Combines the power of API Search and Vector Search with cross-encoder reranking for optimal results.
              </p>
              <div class="bg-white rounded-lg p-4 space-y-2">
                <div class="flex items-center gap-2">
                  <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                  <span class="text-sm">Structured filters (price, location, type)</span>
                </div>
                <div class="flex items-center gap-2">
                  <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                  <span class="text-sm">Semantic understanding (description, features)</span>
                </div>
                <div class="flex items-center gap-2">
                  <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                  <span class="text-sm">Cross-encoder reranking for relevance</span>
                </div>
              </div>
            </div>

            <!-- API Only -->
            <div class="bg-white rounded-xl p-6 border">
              <h2 class="text-xl font-semibold text-gray-800 mb-4">API Only Search</h2>
              <p class="text-gray-600 mb-4">
                Direct search to Property API with structured filters. Suitable for queries with specific criteria.
              </p>
              <div class="bg-gray-50 rounded-lg p-4 space-y-2">
                <div class="flex items-center gap-2">
                  <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                  <span class="text-sm">Fast response time</span>
                </div>
                <div class="flex items-center gap-2">
                  <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                  <span class="text-sm">Exact filter matching</span>
                </div>
                <div class="flex items-center gap-2">
                  <svg class="w-5 h-5 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                  <span class="text-sm">Limited semantic understanding</span>
                </div>
              </div>
            </div>

            <!-- Vector Only -->
            <div class="bg-white rounded-xl p-6 border">
              <h2 class="text-xl font-semibold text-gray-800 mb-4">Vector Only Search</h2>
              <p class="text-gray-600 mb-4">
                Semantic search using ChromaDB with embeddings. Suitable for descriptive queries and natural language.
              </p>
              <div class="bg-gray-50 rounded-lg p-4 space-y-2">
                <div class="flex items-center gap-2">
                  <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                  <span class="text-sm">Natural language understanding</span>
                </div>
                <div class="flex items-center gap-2">
                  <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                  <span class="text-sm">Semantic similarity matching</span>
                </div>
                <div class="flex items-center gap-2">
                  <svg class="w-5 h-5 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                  <span class="text-sm">Requires pre-indexed data</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Agent Tools -->
          <div>
            <h2 class="text-lg font-semibold text-gray-800 mb-4">Agent Tools</h2>
            <p class="text-gray-600 mb-4">The ReAct Agent is equipped with 9 tools to handle various types of queries:</p>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div class="bg-gray-50 rounded-lg p-3 flex items-center gap-3">
                <span class="bg-purple-100 text-purple-800 px-2 py-1 rounded text-xs font-mono">search_properties</span>
              </div>
              <div class="bg-gray-50 rounded-lg p-3 flex items-center gap-3">
                <span class="bg-purple-100 text-purple-800 px-2 py-1 rounded text-xs font-mono">search_nearby</span>
              </div>
              <div class="bg-gray-50 rounded-lg p-3 flex items-center gap-3">
                <span class="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-mono">geocode_location</span>
              </div>
              <div class="bg-gray-50 rounded-lg p-3 flex items-center gap-3">
                <span class="bg-amber-100 text-amber-800 px-2 py-1 rounded text-xs font-mono">search_knowledge</span>
              </div>
              <div class="bg-gray-50 rounded-lg p-3 flex items-center gap-3">
                <span class="bg-pink-100 text-pink-800 px-2 py-1 rounded text-xs font-mono">rerank_results</span>
              </div>
              <div class="bg-gray-50 rounded-lg p-3 flex items-center gap-3">
                <span class="bg-cyan-100 text-cyan-800 px-2 py-1 rounded text-xs font-mono">get_property_details</span>
              </div>
              <div class="bg-gray-50 rounded-lg p-3 flex items-center gap-3">
                <span class="bg-emerald-100 text-emerald-800 px-2 py-1 rounded text-xs font-mono">get_property_types</span>
              </div>
              <div class="bg-gray-50 rounded-lg p-3 flex items-center gap-3">
                <span class="bg-rose-100 text-rose-800 px-2 py-1 rounded text-xs font-mono">get_locations</span>
              </div>
              <div class="bg-gray-50 rounded-lg p-3 flex items-center gap-3">
                <span class="bg-indigo-100 text-indigo-800 px-2 py-1 rounded text-xs font-mono">no_properties_found</span>
              </div>
            </div>
          </div>
        </section>

        <!-- Evaluation Results -->
        <section v-else-if="activeSection === 'evaluation'" class="space-y-8">
          <div>
            <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 mb-4">Evaluation Results</h1>
            <p class="text-gray-600 leading-relaxed">
              Evaluation was conducted on 30 test queries using Constraint-based Evaluation method to measure the accuracy of each search method.
            </p>
          </div>

          <!-- Summary Metrics -->
          <div class="bg-gradient-to-r from-emerald-50 to-teal-50 rounded-xl p-6 border border-emerald-200">
            <h2 class="text-lg font-semibold text-gray-800 mb-4">Summary Metrics</h2>
            <div class="overflow-x-auto">
              <table class="w-full text-sm">
                <thead>
                  <tr class="border-b">
                    <th class="text-left py-2 font-semibold text-gray-700">Method</th>
                    <th class="text-center py-2 font-semibold text-gray-700">Query Success</th>
                    <th class="text-center py-2 font-semibold text-gray-700">Mean CPR</th>
                    <th class="text-center py-2 font-semibold text-gray-700">Strict Success</th>
                  </tr>
                </thead>
                <tbody>
                  <tr class="border-b bg-emerald-100">
                    <td class="py-3 font-medium text-emerald-800">Hybrid</td>
                    <td class="text-center py-3 font-bold text-emerald-700">100%</td>
                    <td class="text-center py-3">97.61%</td>
                    <td class="text-center py-3">96.62%</td>
                  </tr>
                  <tr class="border-b">
                    <td class="py-3 font-medium text-gray-700">API Only</td>
                    <td class="text-center py-3">73.33%</td>
                    <td class="text-center py-3">73.35%</td>
                    <td class="text-center py-3">72.62%</td>
                  </tr>
                  <tr>
                    <td class="py-3 font-medium text-gray-700">Vector Only</td>
                    <td class="text-center py-3">50%</td>
                    <td class="text-center py-3">55.33%</td>
                    <td class="text-center py-3">33.04%</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p class="text-xs text-gray-500 mt-4">
              * Query Success = percentage of queries achieving CPR ≥ 0.60 threshold<br>
              * Mean CPR = average Constraint Pass Rate across all queries<br>
              * Strict Success = ratio of listings where all constraints are satisfied
            </p>
          </div>

          <!-- Visual Comparison Bar Chart -->
          <div>
            <h2 class="text-lg font-semibold text-gray-800 mb-4">Visual Comparison</h2>
            <div class="space-y-4">
              <!-- Hybrid -->
              <div>
                <div class="flex justify-between text-sm mb-1">
                  <span class="font-medium text-gray-700">Hybrid</span>
                  <span class="text-emerald-600 font-bold">100%</span>
                </div>
                <div class="h-4 bg-gray-200 rounded-full overflow-hidden">
                  <div class="h-full bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full" style="width: 100%"></div>
                </div>
              </div>
              <!-- API Only -->
              <div>
                <div class="flex justify-between text-sm mb-1">
                  <span class="font-medium text-gray-700">API Only</span>
                  <span class="text-blue-600 font-bold">73.33%</span>
                </div>
                <div class="h-4 bg-gray-200 rounded-full overflow-hidden">
                  <div class="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full" style="width: 73.33%"></div>
                </div>
              </div>
              <!-- Vector Only -->
              <div>
                <div class="flex justify-between text-sm mb-1">
                  <span class="font-medium text-gray-700">Vector Only</span>
                  <span class="text-purple-600 font-bold">50%</span>
                </div>
                <div class="h-4 bg-gray-200 rounded-full overflow-hidden">
                  <div class="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full" style="width: 50%"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Confusion Matrix -->
          <div>
            <h2 class="text-lg font-semibold text-gray-800 mb-4">Confusion Matrix (Hybrid)</h2>
            <div class="bg-white border rounded-lg p-4 overflow-x-auto">
              <table class="w-full text-sm">
                <thead>
                  <tr>
                    <th class="p-2"></th>
                    <th class="p-2 text-center text-gray-600">Predicted Negative</th>
                    <th class="p-2 text-center text-gray-600">Predicted Positive</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td class="p-2 font-medium text-gray-600">Actual Negative</td>
                    <td class="p-2 text-center bg-green-100 text-green-800 font-bold">TN: 2</td>
                    <td class="p-2 text-center bg-red-100 text-red-800">FP: 0</td>
                  </tr>
                  <tr>
                    <td class="p-2 font-medium text-gray-600">Actual Positive</td>
                    <td class="p-2 text-center bg-red-100 text-red-800">FN: 0</td>
                    <td class="p-2 text-center bg-green-100 text-green-800 font-bold">TP: 28</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p class="text-xs text-gray-500 mt-2">
              Evaluated on 30 gold-labeled queries (28 positive, 2 negative). Hybrid achieved perfect classification with 100% accuracy.
            </p>
          </div>

          <!-- Statistical Tests -->
          <div>
            <h2 class="text-lg font-semibold text-gray-800 mb-4">Statistical Significance Tests</h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div class="bg-gray-50 rounded-lg p-4">
                <h3 class="font-medium text-gray-700 mb-2">Wilcoxon Signed-Rank Test</h3>
                <p class="text-sm text-gray-600">p-value &lt; 0.05: Significant difference between Hybrid vs other methods</p>
              </div>
              <div class="bg-gray-50 rounded-lg p-4">
                <h3 class="font-medium text-gray-700 mb-2">McNemar's Test</h3>
                <p class="text-sm text-gray-600">p-value &lt; 0.05: Hybrid significantly outperforms both API-only and Vector-only</p>
              </div>
            </div>
          </div>
        </section>

        <!-- API Documentation -->
        <section v-else-if="activeSection === 'api'" class="space-y-8">
          <div>
            <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 mb-4">API Documentation</h1>
            <p class="text-gray-600 leading-relaxed">
              API documentation for integration with the Property Search system.
            </p>
          </div>

          <!-- Chat Endpoint -->
          <div class="bg-white border rounded-xl overflow-hidden">
            <div class="bg-emerald-600 text-white px-4 py-2 flex items-center gap-2">
              <span class="bg-emerald-500 px-2 py-0.5 rounded text-xs font-mono">POST</span>
              <span class="font-mono text-sm">/api/v1/chat/stream</span>
            </div>
            <div class="p-4 space-y-4">
              <div>
                <h3 class="font-semibold text-gray-800 mb-2">Request Body</h3>
                <pre class="bg-gray-900 text-gray-100 rounded-lg p-4 overflow-x-auto text-sm">
{
  "message": "string",
  "session_id": "string (optional)",
  "method": "hybrid | api_only | vector_only"
}</pre>
              </div>
              <div>
                <h3 class="font-semibold text-gray-800 mb-2">Response (SSE Stream)</h3>
                <pre class="bg-gray-900 text-gray-100 rounded-lg p-4 overflow-x-auto text-sm">
data: {"type": "session", "session_id": "..."}
data: {"type": "thinking", "content": "..."}
data: {"type": "tool_call", "name": "...", "arguments": {...}}
data: {"type": "tool_result", "name": "...", "result": {...}}
data: {"type": "content", "content": "..."}
data: {"type": "done"}</pre>
              </div>
            </div>
          </div>

          <!-- Session Management -->
          <div>
            <h2 class="text-lg font-semibold text-gray-800 mb-4">Session Management</h2>
            <div class="bg-gray-50 rounded-lg p-4">
              <ul class="space-y-2 text-sm text-gray-600">
                <li class="flex items-start gap-2">
                  <svg class="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                  <span>Session ID is auto-generated if not provided</span>
                </li>
                <li class="flex items-start gap-2">
                  <svg class="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                  <span>Use the same session_id to continue conversation</span>
                </li>
                <li class="flex items-start gap-2">
                  <svg class="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                  <span>History is stored on the server using SQLite</span>
                </li>
              </ul>
            </div>
          </div>
        </section>

        <!-- Property API Guide -->
        <section v-else-if="activeSection === 'property-api'" class="space-y-8">
          <div>
            <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 mb-4">Property API Integration Guide</h1>
            <p class="text-gray-600 leading-relaxed">
              Guide for integrating property data sources with the RAG Search system.
            </p>
          </div>

          <!-- Required Endpoints -->
          <div>
            <h2 class="text-lg font-semibold text-gray-800 mb-4">Required API Endpoints</h2>
            <div class="space-y-4">
              <div class="bg-white border rounded-lg overflow-hidden">
                <div class="bg-blue-600 text-white px-4 py-2 flex items-center gap-2">
                  <span class="bg-blue-500 px-2 py-0.5 rounded text-xs font-mono">GET</span>
                  <span class="font-mono text-sm">/api/properties</span>
                </div>
                <div class="p-4">
                  <p class="text-sm text-gray-600 mb-2">Main endpoint for searching properties with filters</p>
                  <h4 class="font-medium text-gray-700 text-sm mb-2">Query Parameters:</h4>
                  <ul class="text-sm text-gray-600 space-y-1 ml-4">
                    <li><code class="bg-gray-100 px-1 rounded">listing_type</code> - rent | sale</li>
                    <li><code class="bg-gray-100 px-1 rounded">property_type</code> - house | apartment | etc.</li>
                    <li><code class="bg-gray-100 px-1 rounded">min_price</code>, <code class="bg-gray-100 px-1 rounded">max_price</code></li>
                    <li><code class="bg-gray-100 px-1 rounded">bedrooms</code>, <code class="bg-gray-100 px-1 rounded">bathrooms</code></li>
                    <li><code class="bg-gray-100 px-1 rounded">location</code> - location/area</li>
                    <li><code class="bg-gray-100 px-1 rounded">lat</code>, <code class="bg-gray-100 px-1 rounded">lng</code>, <code class="bg-gray-100 px-1 rounded">radius</code> - nearby search</li>
                  </ul>
                </div>
              </div>

              <div class="bg-white border rounded-lg overflow-hidden">
                <div class="bg-blue-600 text-white px-4 py-2 flex items-center gap-2">
                  <span class="bg-blue-500 px-2 py-0.5 rounded text-xs font-mono">GET</span>
                  <span class="font-mono text-sm">/api/properties/{id}</span>
                </div>
                <div class="p-4">
                  <p class="text-sm text-gray-600">Get complete details of a single property by ID</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Response Format -->
          <div>
            <h2 class="text-lg font-semibold text-gray-800 mb-4">Response Format</h2>
            <pre class="bg-gray-900 text-gray-100 rounded-lg p-4 overflow-x-auto text-sm">
{
  "success": true,
  "data": [
    {
      "id": "string",
      "title": "string",
      "description": "string",
      "price": number,
      "listing_type": "rent | sale",
      "property_type": "house | apartment | ...",
      "bedrooms": number,
      "bathrooms": number,
      "land_area": number,
      "building_area": number,
      "location": {
        "address": "string",
        "city": "string",
        "district": "string",
        "lat": number,
        "lng": number
      },
      "images": ["url1", "url2", ...],
      "url": "string"
    }
  ],
  "meta": {
    "total": number,
    "page": number,
    "per_page": number
  }
}</pre>
          </div>
        </section>

        <!-- Acknowledgements -->
        <section v-else-if="activeSection === 'acknowledgements'" class="space-y-8">
          <div>
            <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 mb-4">Acknowledgements</h1>
            <p class="text-gray-600 leading-relaxed">
              The research and development of this RAG Property Search system would not have been possible without the support from various parties.
            </p>
          </div>

          <!-- Institution -->
          <div class="bg-white border rounded-xl p-6">
            <h2 class="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
              </svg>
              Institution
            </h2>
            <div class="flex items-start gap-4">
              <div class="w-20 h-20 flex-shrink-0 bg-gray-100 rounded-lg flex items-center justify-center overflow-hidden">
                <img src="/binus-logo.png" alt="BINUS University" class="w-full h-full object-contain" @error="$event.target.style.display='none'; $event.target.nextElementSibling.style.display='flex'" />
                <div class="hidden w-full h-full items-center justify-center bg-gradient-to-br from-blue-600 to-blue-800 text-white font-bold text-2xl">
                  BU
                </div>
              </div>
              <div class="space-y-1 text-gray-600">
                <p class="font-semibold text-gray-800">Bina Nusantara University</p>
                <p><strong>Department:</strong> Computer Science</p>
                <p><strong>Program:</strong> BINUS Graduate Program - Master of Computer Science</p>
                <p><strong>Location:</strong> Jakarta, Indonesia 11480</p>
              </div>
            </div>
          </div>

          <!-- Supervisor -->
          <div class="bg-gradient-to-r from-amber-50 to-orange-50 rounded-xl p-6 border border-amber-200">
            <h2 class="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <svg class="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
              </svg>
              Thesis Supervisor
            </h2>
            <div class="bg-white rounded-lg p-4">
              <div class="flex items-center gap-4">
                <div class="w-14 h-14 flex-shrink-0 rounded-full overflow-hidden bg-gradient-to-br from-amber-400 to-orange-500 relative">
                  <img src="/img/supervisor.png" alt="Supervisor" class="w-full h-full object-cover" @error="$event.target.style.display='none'; $event.target.nextElementSibling.style.display='flex'" />
                  <div class="hidden absolute inset-0 items-center justify-center">
                    <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                  </div>
                </div>
                <div>
                  <p class="font-medium text-gray-800">Dr. Suryadiputra Liawatimena, S.Kom, PgDip.App.Sci</p>
                  <p class="text-sm text-gray-600">Thesis Advisor</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Data Provider -->
          <div class="bg-gradient-to-r from-emerald-50 to-teal-50 rounded-xl p-6 border border-emerald-200">
            <h2 class="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <svg class="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"></path>
              </svg>
              Data Provider
            </h2>
            <div class="bg-white rounded-lg p-4">
              <div class="flex items-center gap-3 mb-2">
                <div class="w-10 h-10 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-lg overflow-hidden relative">
                  <img src="/img/metaproperty.png" alt="Meta Property" class="w-full h-full object-contain" @error="$event.target.style.display='none'; $event.target.nextElementSibling.style.display='flex'" />
                  <div class="hidden absolute inset-0 items-center justify-center">
                    <span class="text-white font-bold text-lg">M</span>
                  </div>
                </div>
                <div>
                  <p class="font-medium text-gray-800">PT. Meta Properti Indonesia</p>
                  <p class="text-sm text-gray-600">
                    <a href="https://metaproperty.co.id" target="_blank" class="text-emerald-600 hover:underline">metaproperty.co.id</a>
                  </p>
                </div>
              </div>
              <p class="text-sm text-gray-600 mt-3">
                Property data used in this research is sourced from PT. Meta Properti Indonesia, who provided API access for academic purposes.
              </p>
            </div>
          </div>

          <!-- Technical Support -->
          <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200">
            <h2 class="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path>
              </svg>
              Technical Support
            </h2>
            <div class="bg-white rounded-lg p-4">
              <div class="flex items-center gap-3 mb-2">
                <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg overflow-hidden relative">
                  <img src="/img/bizapps.png" alt="Bizapps" class="w-full h-full object-contain" @error="$event.target.style.display='none'; $event.target.nextElementSibling.style.display='flex'" />
                  <div class="hidden absolute inset-0 items-center justify-center">
                    <span class="text-white font-bold text-lg">B</span>
                  </div>
                </div>
                <div>
                  <p class="font-medium text-gray-800">IT Programmer Bizapps.id</p>
                  <p class="text-sm text-gray-600">Technical Consultant</p>
                </div>
              </div>
              <p class="text-sm text-gray-600 mt-3">
                Special thanks for assistance in finding relevant source code and technical guidance during the development process.
              </p>
            </div>
          </div>

          <!-- AI Development Assistant -->
          <div class="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl p-6 border border-purple-200">
            <h2 class="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
              </svg>
              AI Development Assistant
            </h2>
            <div class="bg-white rounded-lg p-4">
              <div class="flex items-center gap-3 mb-2">
                <div class="w-10 h-10 bg-gradient-to-br from-orange-400 to-amber-500 rounded-lg overflow-hidden relative">
                  <img src="/img/claude.png" alt="Claude" class="w-full h-full object-contain" @error="$event.target.style.display='none'; $event.target.nextElementSibling.style.display='flex'" />
                  <div class="hidden absolute inset-0 items-center justify-center">
                    <span class="text-white font-bold text-lg">C</span>
                  </div>
                </div>
                <div>
                  <p class="font-medium text-gray-800">Claude by Anthropic</p>
                  <p class="text-sm text-gray-600">AI Coding Assistant</p>
                </div>
              </div>
              <p class="text-sm text-gray-600 mt-3">
                The development of this system was assisted by Claude (Anthropic) as an AI coding assistant for code implementation, debugging, and technical documentation.
              </p>
            </div>
          </div>

          <!-- Technology Credits -->
          <div>
            <h2 class="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path>
              </svg>
              Technologies Used
            </h2>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div class="bg-gray-50 rounded-lg p-3 text-center">
                <span class="text-sm font-medium text-gray-700">OpenAI GPT-4</span>
              </div>
              <div class="bg-gray-50 rounded-lg p-3 text-center">
                <span class="text-sm font-medium text-gray-700">Vue.js 3</span>
              </div>
              <div class="bg-gray-50 rounded-lg p-3 text-center">
                <span class="text-sm font-medium text-gray-700">FastAPI</span>
              </div>
              <div class="bg-gray-50 rounded-lg p-3 text-center">
                <span class="text-sm font-medium text-gray-700">ChromaDB</span>
              </div>
              <div class="bg-gray-50 rounded-lg p-3 text-center">
                <span class="text-sm font-medium text-gray-700">Tailwind CSS</span>
              </div>
              <div class="bg-gray-50 rounded-lg p-3 text-center">
                <span class="text-sm font-medium text-gray-700">Sentence Transformers</span>
              </div>
            </div>
          </div>

          <!-- Special Thanks -->
          <div class="bg-gradient-to-r from-rose-50 to-pink-50 rounded-xl p-6 border border-rose-200">
            <h2 class="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <svg class="w-5 h-5 text-rose-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
              </svg>
              Special Thanks
            </h2>
            <div class="bg-white rounded-lg p-4">
              <div class="flex items-center gap-3 mb-2">
                <div class="w-10 h-10 bg-gradient-to-br from-rose-400 to-pink-500 rounded-lg overflow-hidden relative">
                  <img src="/img/family.png" alt="Family" class="w-full h-full object-cover" @error="$event.target.style.display='none'; $event.target.nextElementSibling.style.display='flex'" />
                  <div class="hidden absolute inset-0 items-center justify-center">
                    <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"></path>
                    </svg>
                  </div>
                </div>
                <div>
                  <p class="font-medium text-gray-800">My Beloved Family</p>
                  <p class="text-sm text-gray-600">The Greatest Support</p>
                </div>
              </div>
              <p class="text-sm text-gray-600 mt-3">
                Above all, my deepest gratitude goes to my family for their unconditional love, endless patience, and unwavering support throughout this journey. Their prayers, encouragement, and sacrifices have been the foundation of everything I have achieved.
              </p>
            </div>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineEmits(['back-to-chat'])

const activeSection = ref('overview')
const showMobileNav = ref(false)

const sections = [
  {
    id: 'overview',
    title: 'System Overview',
    icon: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>'
  },
  {
    id: 'methods',
    title: 'Search Methods',
    icon: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>'
  },
  {
    id: 'evaluation',
    title: 'Evaluation Results',
    icon: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>'
  },
  {
    id: 'api',
    title: 'API Documentation',
    icon: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path></svg>'
  },
  {
    id: 'property-api',
    title: 'Property API Guide',
    icon: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>'
  },
  {
    id: 'acknowledgements',
    title: 'Acknowledgements',
    icon: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path></svg>'
  }
]
</script>

<style scoped>
pre {
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
