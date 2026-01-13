import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { OptimizationJob, OptimizationConfig, OptimizationResults } from '../types';
import optimizationService from '../services/optimizationService';

interface OptimizationState {
  jobs: OptimizationJob[];
  currentJob: OptimizationJob | null;
  results: OptimizationResults | null;
  isLoading: boolean;
  error: string | null;
  isRunning: boolean;
}

const initialState: OptimizationState = {
  jobs: [],
  currentJob: null,
  results: null,
  isLoading: false,
  error: null,
  isRunning: false,
};

// Async thunks
export const createOptimizationJob = createAsyncThunk(
  'optimization/createJob',
  async (data: {
    name: string;
    config: OptimizationConfig;
    project_ids: string[];
  }) => {
    const response = await optimizationService.createOptimizationJob(data);
    return response;
  }
);

export const fetchOptimizationJobs = createAsyncThunk(
  'optimization/fetchJobs',
  async (params?: { skip?: number; limit?: number; status?: string }) => {
    const response = await optimizationService.getOptimizationJobs(params);
    return response;
  }
);

export const fetchOptimizationJob = createAsyncThunk(
  'optimization/fetchJob',
  async (id: string) => {
    const response = await optimizationService.getOptimizationJob(id);
    return response;
  }
);

export const fetchJobStatus = createAsyncThunk(
  'optimization/fetchJobStatus',
  async (id: string) => {
    const response = await optimizationService.getJobStatus(id);
    return { id, ...response };
  }
);

export const fetchJobResults = createAsyncThunk(
  'optimization/fetchJobResults',
  async (id: string) => {
    const response = await optimizationService.getJobResults(id);
    return response;
  }
);

export const cancelJob = createAsyncThunk(
  'optimization/cancelJob',
  async (id: string) => {
    await optimizationService.cancelJob(id);
    return id;
  }
);

export const runQuickOptimization = createAsyncThunk(
  'optimization/runQuick',
  async (project_ids: string[]) => {
    const response = await optimizationService.runQuickOptimization(project_ids);
    return response;
  }
);

export const runGreenfieldOptimization = createAsyncThunk(
  'optimization/runGreenfield',
  async () => {
    const response = await optimizationService.runGreenfieldOptimization();
    return response;
  }
);

// Slice
const optimizationSlice = createSlice({
  name: 'optimization',
  initialState,
  reducers: {
    setCurrentJob: (state, action: PayloadAction<OptimizationJob | null>) => {
      state.currentJob = action.payload;
      state.isRunning = action.payload?.status === 'running';
    },
    clearResults: (state) => {
      state.results = null;
    },
    clearError: (state) => {
      state.error = null;
    },
    updateJobProgress: (state, action: PayloadAction<{ id: string; progress: number }>) => {
      const job = state.jobs.find((j) => j.id === action.payload.id);
      if (job) {
        job.progress_percentage = action.payload.progress;
      }
      if (state.currentJob?.id === action.payload.id) {
        state.currentJob.progress_percentage = action.payload.progress;
      }
    },
  },
  extraReducers: (builder) => {
    // Create optimization job
    builder
      .addCase(createOptimizationJob.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(createOptimizationJob.fulfilled, (state, action) => {
        state.isLoading = false;
        state.jobs.unshift(action.payload);
        state.currentJob = action.payload;
        state.isRunning = action.payload.status === 'running';
      })
      .addCase(createOptimizationJob.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to create optimization job';
      });

    // Fetch optimization jobs
    builder
      .addCase(fetchOptimizationJobs.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchOptimizationJobs.fulfilled, (state, action) => {
        state.isLoading = false;
        state.jobs = action.payload;
      })
      .addCase(fetchOptimizationJobs.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to fetch optimization jobs';
      });

    // Fetch single optimization job
    builder
      .addCase(fetchOptimizationJob.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchOptimizationJob.fulfilled, (state, action) => {
        state.isLoading = false;
        state.currentJob = action.payload;
        state.isRunning = action.payload.status === 'running';
      })
      .addCase(fetchOptimizationJob.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to fetch optimization job';
      });

    // Fetch job status
    builder
      .addCase(fetchJobStatus.fulfilled, (state, action) => {
        const job = state.jobs.find((j) => j.id === action.payload.id);
        if (job) {
          job.status = action.payload.status as any;
          job.progress_percentage = action.payload.progress_percentage;
        }
        if (state.currentJob?.id === action.payload.id) {
          state.currentJob.status = action.payload.status as any;
          state.currentJob.progress_percentage = action.payload.progress_percentage;
          state.isRunning = action.payload.status === 'running';
        }
      });

    // Fetch job results
    builder
      .addCase(fetchJobResults.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchJobResults.fulfilled, (state, action) => {
        state.isLoading = false;
        state.results = action.payload;
      })
      .addCase(fetchJobResults.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to fetch job results';
      });

    // Cancel job
    builder
      .addCase(cancelJob.fulfilled, (state, action) => {
        const job = state.jobs.find((j) => j.id === action.payload);
        if (job) {
          job.status = 'cancelled' as any;
        }
        if (state.currentJob?.id === action.payload) {
          state.currentJob.status = 'cancelled' as any;
          state.isRunning = false;
        }
      });

    // Quick optimization
    builder
      .addCase(runQuickOptimization.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(runQuickOptimization.fulfilled, (state, action) => {
        state.isLoading = false;
        state.jobs.unshift(action.payload);
        state.currentJob = action.payload;
        state.results = action.payload.results || null;
        state.isRunning = action.payload.status === 'running';
      })
      .addCase(runQuickOptimization.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to run optimization';
      });

    // Greenfield optimization
    builder
      .addCase(runGreenfieldOptimization.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(runGreenfieldOptimization.fulfilled, (state, action) => {
        state.isLoading = false;
        state.jobs.unshift(action.payload);
        state.currentJob = action.payload;
        state.results = action.payload.results || null;
        state.isRunning = action.payload.status === 'running';
      })
      .addCase(runGreenfieldOptimization.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Failed to run greenfield optimization';
      });
  },
});

export const {
  setCurrentJob,
  clearResults,
  clearError,
  updateJobProgress,
} = optimizationSlice.actions;

export default optimizationSlice.reducer;
