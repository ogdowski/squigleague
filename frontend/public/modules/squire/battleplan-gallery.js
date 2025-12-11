/**
 * Battle Plan Gallery Component
 * Displays all Age of Sigmar battle plans with deployment maps
 */

class BattlePlanGallery {
    constructor() {
        this.battlePlans = [];
        this.loading = true;
        this.error = null;
        this.selectedPlan = null;
    }

    async loadBattlePlans() {
        try {
            this.loading = true;
            this.error = null;
            
            const response = await fetch(`${window.API_BASE_URL}/api/squire/battle-plans/gallery?system=age_of_sigmar`);
            
            if (!response.ok) {
                throw new Error(`Failed to load battle plans: ${response.statusText}`);
            }
            
            this.battlePlans = await response.json();
            this.loading = false;
        } catch (err) {
            console.error('Error loading battle plans:', err);
            this.error = err.message;
            this.loading = false;
        }
    }

    selectPlan(plan) {
        this.selectedPlan = plan;
    }

    closeModal() {
        this.selectedPlan = null;
    }

    init() {
        return {
            gallery: this,
            
            async init() {
                await this.gallery.loadBattlePlans();
            },
            
            get battlePlans() {
                return this.gallery.battlePlans;
            },
            
            get loading() {
                return this.gallery.loading;
            },
            
            get error() {
                return this.gallery.error;
            },
            
            get selectedPlan() {
                return this.gallery.selectedPlan;
            },
            
            selectPlan(plan) {
                this.gallery.selectPlan(plan);
            },
            
            closeModal() {
                this.gallery.closeModal();
            }
        };
    }
}

// Export for Alpine.js
window.BattlePlanGallery = BattlePlanGallery;
