public class Main {
    public static int binarySearch(int[] arr, int target) {
        int lo = 0, hi = arr.length - 1;
        while (lo <= hi) {
            int mid = (lo + hi) >>> 1;
            if (arr[mid] == target) return mid;
            if (arr[mid] < target) lo = mid + 1;
            else hi = mid - 1;
        }
        return -1;
    }

    public static void main(String[] args) {
        int[] arr = {4, 8, 15, 16, 23, 42, 99};
        System.out.println("Target 23 found at index: " + binarySearch(arr, 23));
    }
}
