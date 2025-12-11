/**
 * Battle Plan Gallery Page Renderer
 * Renders the gallery view with all AoS battle plan deployment maps
 */

window.renderBattlePlanGallery = function() {
    return `
        <div class="min-h-screen bg-bg-darkest py-8 px-4" x-data="(new BattlePlanGallery()).init()">
            <div class="max-w-7xl mx-auto">
                <!-- Header -->
                <div class="text-center mb-8">
                    <h1 class="text-4xl font-montserrat font-bold text-primary mb-2">
                        Age of Sigmar Battle Plans
                    </h1>
                    <p class="text-text-secondary">
                        General's Handbook 2025-2026 Deployment Maps
                    </p>
                    <p class="text-sm text-text-muted mt-2">
                        Source: <a href="https://wahapedia.ru/aos4/the-rules/general-s-handbook-2025-26/" target="_blank" class="text-accent-light hover:text-accent-mid underline">Wahapedia</a>
                    </p>
                </div>

                <!-- Loading State -->
                <div x-show="loading" class="text-center py-20">
                    <div class="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
                    <p class="mt-4 text-text-secondary">Loading battle plans...</p>
                </div>

                <!-- Error State -->
                <div x-show="error" class="max-w-2xl mx-auto bg-red-900/20 border border-red-900 rounded-lg p-6 text-center">
                    <p class="text-red-400 mb-2">Failed to load battle plans</p>
                    <p class="text-text-muted text-sm" x-text="error"></p>
                    <button @click="gallery.loadBattlePlans()" class="mt-4 px-4 py-2 bg-primary hover:bg-primary-dark text-bg-darkest font-semibold rounded transition">
                        Retry
                    </button>
                </div>

                <!-- Gallery Grid -->
                <div x-show="!loading && !error" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    <template x-for="plan in battlePlans" :key="plan.name">
                        <div 
                            @click="selectPlan(plan)"
                            class="bg-bg-darker border border-bg-dark rounded-lg overflow-hidden hover:border-primary transition-all cursor-pointer shadow-lg hover:shadow-primary/20"
                        >
                            <!-- Deployment Map Image -->
                            <div class="aspect-square bg-bg-dark flex items-center justify-center overflow-hidden">
                                <template x-if="plan.deployment_map_url">
                                    <img 
                                        :src="plan.deployment_map_url" 
                                        :alt="plan.name + ' deployment map'"
                                        class="w-full h-full object-contain hover:scale-105 transition-transform"
                                        loading="lazy"
                                    />
                                </template>
                                <template x-if="!plan.deployment_map_url">
                                    <div class="text-text-muted text-center p-4">
                                        <svg class="w-16 h-16 mx-auto mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                        </svg>
                                        <p class="text-sm">No map available</p>
                                    </div>
                                </template>
                            </div>
                            
                            <!-- Battle Plan Name -->
                            <div class="p-4">
                                <h3 class="text-lg font-montserrat font-bold text-text-primary text-center" x-text="plan.name"></h3>
                                <p class="text-sm text-text-secondary text-center mt-1" x-text="plan.deployment_description"></p>
                            </div>
                        </div>
                    </template>
                </div>

                <!-- Modal for Battle Plan Details -->
                <div 
                    x-show="selectedPlan" 
                    @click.self="closeModal()"
                    class="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
                    x-transition
                >
                    <div 
                        class="bg-bg-darker border border-primary rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl"
                        @click.stop
                    >
                        <template x-if="selectedPlan">
                            <div>
                                <!-- Modal Header -->
                                <div class="sticky top-0 bg-bg-darker border-b border-bg-dark p-6 flex items-center justify-between z-10">
                                    <h2 class="text-2xl font-montserrat font-bold text-primary" x-text="selectedPlan.name"></h2>
                                    <button 
                                        @click="closeModal()"
                                        class="text-text-muted hover:text-text-primary transition"
                                    >
                                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                    </button>
                                </div>

                                <!-- Modal Content -->
                                <div class="p-6">
                                    <!-- Deployment Map -->
                                    <div class="mb-6 bg-bg-dark rounded-lg overflow-hidden">
                                        <img 
                                            :src="selectedPlan.deployment_map_url" 
                                            :alt="selectedPlan.name + ' deployment map'"
                                            class="w-full"
                                        />
                                    </div>

                                    <!-- Battle Plan Details -->
                                    <div class="space-y-4">
                                        <div>
                                            <h3 class="text-sm font-semibold text-text-secondary uppercase mb-1">Deployment</h3>
                                            <p class="text-text-primary" x-text="selectedPlan.deployment_description"></p>
                                        </div>

                                        <div>
                                            <h3 class="text-sm font-semibold text-text-secondary uppercase mb-1">Primary Objective</h3>
                                            <p class="text-text-primary" x-text="selectedPlan.primary_objective"></p>
                                        </div>

                                        <div>
                                            <h3 class="text-sm font-semibold text-text-secondary uppercase mb-1">Victory Conditions</h3>
                                            <p class="text-text-primary" x-text="selectedPlan.victory_conditions"></p>
                                        </div>

                                        <div x-show="selectedPlan.special_rules && selectedPlan.special_rules.length > 0">
                                            <h3 class="text-sm font-semibold text-text-secondary uppercase mb-2">Special Rules</h3>
                                            <ul class="list-disc list-inside space-y-1">
                                                <template x-for="rule in selectedPlan.special_rules" :key="rule">
                                                    <li class="text-text-primary" x-text="rule"></li>
                                                </template>
                                            </ul>
                                        </div>

                                        <div>
                                            <h3 class="text-sm font-semibold text-text-secondary uppercase mb-1">Turn Limit</h3>
                                            <p class="text-text-primary" x-text="selectedPlan.turn_limit + ' rounds'"></p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </template>
                    </div>
                </div>
            </div>
        </div>
    `;
};
